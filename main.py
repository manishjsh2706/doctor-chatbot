from flask import Flask, request, jsonify
import json
from services.openai_service import call_openai
from services.appointment_service import (
    handle_check_doctor_availability,
    handle_book_appointment
)

app = Flask(__name__)

conversation_history = []
pending_booking = {}

functions = [
    {
        "name": "check_doctor_availability",
        "description": "Check availability based on doctor name or specialty",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_name": {"type": "string"},
                "date": {"type": "string"},
                "time": {"type": "string"}
            },
            "required": ["doctor_name"]
        }
    },
    {
        "name": "book_appointment",
        "description": "Book an appointment with a doctor",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_name": {"type": "string"},
                "date": {"type": "string"},
                "time": {"type": "string"},
                "patient_name": {"type": "string"}
            },
            "required": ["doctor_name", "date", "time", "patient_name"]
        }
    }
]

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history, pending_booking
    print('In chat function')

    user_message = request.json.get("message").strip()

    # ==================================================================
    # 1. USER PROVIDING DATE, TIME, NAME (after doctor selected)
    # ==================================================================
    if pending_booking.get("awaiting_date_time"):
        try:
            date, time, patient_name = [x.strip() for x in user_message.split(",")]
        except:
            return jsonify({"reply": "Invalid format. Use: YYYY-MM-DD, HH:MM, Name"})

        params = {
            "doctor_name": pending_booking["doctor_name"],
            "date": date,
            "time": time,
            "patient_name": patient_name
        }

        result = handle_book_appointment(params)

        # Slot unavailable → show available slots
        if result.get("slot_available") is False:
            slots = "\n".join(f"- {slot}" for slot in result["available_slots"])

            pending_booking = {
                "doctor_name": pending_booking["doctor_name"],
                "awaiting_slot_selection": True
            }

            reply = (
                "This slot is not available.\n"
                f"Here are available slots for {pending_booking['doctor_name']}:\n"
                f"{slots}\n"
                "Please choose a slot using: YYYY-MM-DD, HH:MM"
            )
            return jsonify({"reply": reply})

        # Slot is available → booking success
        pending_booking.clear()
        conversation_history.clear()

        reply = result["message"] + "\nIs there anything else I can help you with?"
        return jsonify({"reply": reply})

    # ==================================================================
    # 2. USER SELECTING ALTERNATE SLOT
    # ==================================================================
    if pending_booking.get("awaiting_slot_selection"):
        try:
            date, time = [x.strip() for x in user_message.split(",")]
        except:
            return jsonify({"reply": "Invalid format. Use: YYYY-MM-DD, HH:MM"})

        pending_booking = {
            "doctor_name": pending_booking["doctor_name"],
            "date": date,
            "time": time,
            "awaiting_name": True
        }

        return jsonify({"reply": "Great! Please tell me the patient's name."})

    # ==================================================================
    # 3. USER PROVIDING PATIENT NAME
    # ==================================================================
    if pending_booking.get("awaiting_name"):
        params = {
            "doctor_name": pending_booking["doctor_name"],
            "date": pending_booking["date"],
            "time": pending_booking["time"],
            "patient_name": user_message
        }

        result = handle_book_appointment(params)

        pending_booking.clear()
        conversation_history.clear()

        reply = result["message"] + "\nIs there anything else I can help you with?"
        return jsonify({"reply": reply})

    # ==================================================================
    # 4. USER CHOOSING DOCTOR FROM SPECIALTY
    # ==================================================================
    if pending_booking.get("choose_doctor"):
        selected_doctor = user_message.strip()

        pending_booking = {
            "doctor_name": selected_doctor,
            "awaiting_date_time": True
        }

        reply = (
            f"Great! You selected {selected_doctor}.\n"
            "Please provide date, time, and your name.\n"
            "Format: YYYY-MM-DD, HH:MM, YourName"
        )
        return jsonify({"reply": reply})

    # ==================================================================
    # 5. DIRECT DOCTOR NAME DETECTION
    # ==================================================================
    if user_message.lower().startswith("dr.") or "dr." in user_message.lower():

        doctor_name = user_message.replace("I want to book appointment of", "").strip()

        # Check only the doctor name first
        params = {"doctor_name": doctor_name, "date": "", "time": ""}
        result = handle_check_doctor_availability(params)

        # If specialty detected → list doctors
        if result.get("choose_doctor"):
            pending_booking = {"choose_doctor": True}
            return jsonify({"reply": result["message"]})

        # Ask user for date/time/name
        pending_booking = {
            "doctor_name": doctor_name,
            "awaiting_date_time": True
        }

        reply = (
            f"Please provide the date, time, and patient name for {doctor_name}.\n"
            "Format: YYYY-MM-DD, HH:MM, Name"
        )
        return jsonify({"reply": reply})

    # ==================================================================
    # 6. SYMPTOM FLOW → Specialty detection
    # ==================================================================
    conversation_history.append({"role": "user", "content": user_message})

    messages = [
        {
            "role": "system",
            "content":
            "You are a medical clinic assistant. RULES:\n"
            "-----------------------------\n"
            "SYMPTOM → SPECIALTY MAPPING:\n"
            "- rashes, itching, skin issues → Dermatologist\n"
            "- ankle pain, leg pain, joint injury, bone pain, swelling → Orthopedic\n"
            "- chest pain, heart discomfort → Cardiologist\n"
            "- fever, cold, flu, headache → General Physician\n"
            "-----------------------------\n"
            "LOGIC:\n"
            "1. If user names a doctor → skip symptoms and go to booking.\n"
            "2. If user describes symptoms → detect correct specialty using mapping above.\n"
            "3. Then call check_doctor_availability with the SPECIALTY as doctor_name.\n"
            "4. If multiple doctors exist → list them → ask user to choose.\n"
            "5. After doctor selection → ask for date/time/name.\n"
            "6. If slot unavailable → show all available slots.\n"
            "7. Never ask for symptoms if doctor name is provided."

        }
    ]
    messages.extend(conversation_history)

    response = call_openai(messages, functions=functions)

    # ==================================================================
    # 7. FUNCTION HANDLING
    # ==================================================================
    if response.finish_reason == "function_call":
        fn = response.message.function_call
        params = json.loads(fn.arguments)

        # CHECK AVAILABILITY
        if fn.name == "check_doctor_availability":
            result = handle_check_doctor_availability(params)

            # Specialty → choose doctor
            if result.get("choose_doctor"):
                pending_booking = {"choose_doctor": True}
                return jsonify({"reply": result["message"]})

            # Doctor exists but user hasn't given date/time yet
            if result.get("available") is None:
                pending_booking = {
                    "doctor_name": result["doctor_name"],
                    "awaiting_date_time": True
                }
                reply = (
                    f"Please provide the date, time, and patient name for {result['doctor_name']}.\n"
                    "Format: YYYY-MM-DD, HH:MM, Name"
                )
                return jsonify({"reply": reply})

            # No slots left at all
            if result.get("date") is None:
                return jsonify({"reply": result["message"]})

            # Slot exists
            if result["available"]:
                pending_booking = {
                    "doctor_name": result["doctor_name"],
                    "date": result["date"],
                    "time": result["time"],
                    "awaiting_name": False
                }
                reply = (
                    f"Yes, {result['doctor_name']} is available on "
                    f"{result['date']} at {result['time']}.\n"
                    "Do you want to book?"
                )
                return jsonify({"reply": reply})

            # Slot unavailable → next best slot
            pending_booking = {
                "doctor_name": result["doctor_name"],
                "date": result["date"],
                "time": result["time"],
                "awaiting_name": False
            }

            reply = (
                f"{result['doctor_name']} is not available at that time.\n"
                f"Next available slot: {result['date']} at {result['time']}.\n"
                "Do you want to book?"
            )
            return jsonify({"reply": reply})

        # BOOK APPOINTMENT
        if fn.name == "book_appointment":
            result = handle_book_appointment(params)

            # Slot unavailable → list all available
            if result.get("slot_available") is False:
                slots = "\n".join(f"- {slot}" for slot in result["available_slots"])

                pending_booking = {
                    "doctor_name": result["doctor_name"],
                    "awaiting_slot_selection": True
                }

                reply = (
                    "This slot is not available.\n"
                    f"Available time slots for {result['doctor_name']}:\n"
                    f"{slots}\nPlease choose in format YYYY-MM-DD, HH:MM"
                )
                return jsonify({"reply": reply})

            # Successful booking
            pending_booking.clear()
            conversation_history.clear()

            reply = result["message"] + "\nIs there anything else I can help you with?"
            return jsonify({"reply": reply})

    # ==================================================================
    # NORMAL RESPONSE
    # ==================================================================
    return jsonify({"reply": response.message.content})


if __name__ == "__main__":
   # app.run(debug=True)
   app.run(host="0.0.0.0", port=5000, debug=True)
