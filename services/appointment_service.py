import json
from db.doctors_repository import (
    get_doctor_by_name,
    get_doctors_by_specialty,
    get_available_slot,
    get_first_available_slot,
    get_availability,
    book_slot,
    create_appointment
)

# ------------------------------------------------------------
# SPECIALTY + AVAILABILITY HANDLING
# ------------------------------------------------------------
def handle_check_doctor_availability(params):
    doctor_name = params.get("doctor_name")
    date = params.get("date")
    time = params.get("time")

    # ------------------------------------------------------------
    # 1. SPECIALTY DETECTION (Dermatologist → list multiple doctors)
    # ------------------------------------------------------------
    doctors_in_specialty = get_doctors_by_specialty(doctor_name)

    if doctors_in_specialty and len(doctors_in_specialty) > 1:
        doctor_list = "\n".join(f"- {row[1]}" for row in doctors_in_specialty)
        return {
            "choose_doctor": True,
            "message": (
                f"You should see a {doctor_name}. Here are the available doctors:\n"
                f"{doctor_list}\nPlease tell me which doctor you prefer."
            )
        }

    # Exactly one doctor for specialty
    if doctors_in_specialty and len(doctors_in_specialty) == 1:
        doctor_name = doctors_in_specialty[0][1]

    # ------------------------------------------------------------
    # 2. LOOKUP DOCTOR BY NAME
    # ------------------------------------------------------------
    doctor = get_doctor_by_name(doctor_name)

    if not doctor:
        return {
            "available": False,
            "doctor_name": doctor_name,
            "date": None,
            "time": None,
            "message": f"No doctor found with the name {doctor_name}."
        }

    doctor_id = doctor[0]

    # ------------------------------------------------------------
    # IMPORTANT FIX: If user has NOT given date/time yet, just confirm doctor is valid
    # ------------------------------------------------------------
    if not date or not time:
        return {
            "available": None,        # Neither available nor unavailable → waiting for date/time
            "doctor_name": doctor_name,
            "date": None,
            "time": None
        }

    # ------------------------------------------------------------
    # 3. CHECK REQUESTED SLOT
    # ------------------------------------------------------------
    req_slot = get_available_slot(doctor_id, date, time)
    if req_slot:
        return {
            "available": True,
            "doctor_name": doctor_name,
            "date": date,
            "time": time
        }

    # ------------------------------------------------------------
    # 4. SUGGEST NEXT AVAILABLE SLOT
    # ------------------------------------------------------------
    next_slot = get_first_available_slot(doctor_id)
    if next_slot:
        return {
            "available": False,
            "doctor_name": doctor_name,
            "date": str(next_slot[0]),
            "time": str(next_slot[1]),
            "message": "Requested slot unavailable. Suggesting next available."
        }

    # ------------------------------------------------------------
    # 5. NO SLOTS AT ALL
    # ------------------------------------------------------------
    return {
        "available": False,
        "doctor_name": doctor_name,
        "date": None,
        "time": None,
        "message": f"No available slots left for {doctor_name}."
    }


# ------------------------------------------------------------
# BOOK APPOINTMENT (supports fallback slot selection)
# ------------------------------------------------------------
def handle_book_appointment(params):
    doctor_name = params.get("doctor_name")
    date = params.get("date")
    time = params.get("time")
    patient_name = params.get("patient_name")

    print(f"--- doctor_name: '{doctor_name}' ---")
    print(f"--- date: '{date}' ---")
    print(f"--- time: '{time}' ---")
    print(f"--- patient_name: '{patient_name}' ---")

    doctor = get_doctor_by_name(doctor_name)

    if not doctor:
        return {
            "error": True,
            "message": f"No doctor found with the name {doctor_name}."
        }

    doctor_id = doctor[0]

    # ------------------------------------------------------------
    # 1. Requested slot available?
    # ------------------------------------------------------------
    slot = get_available_slot(doctor_id, date, time)

    if not slot:
        all_slots = get_availability(doctor_id)

        free_slots = [
            f"{str(s[0])}, {str(s[1])}"
            for s in all_slots
            if s[2] is False
        ]

        if not free_slots:
            return {
                "error": True,
                "message": f"No available slots found for {doctor_name}."
            }

        return {
            "slot_available": False,
            "doctor_name": doctor_name,
            "message": "This slot is not available.",
            "available_slots": free_slots
        }

    # ------------------------------------------------------------
    # 2. BOOK SLOT
    # ------------------------------------------------------------
    book_slot(slot[0])
    create_appointment(doctor_id, patient_name, date, time)

    return {
        "slot_available": True,
        "message": (
            f"Your appointment with {doctor_name} "
            f"is confirmed on {date} at {time}."
        )
    }
