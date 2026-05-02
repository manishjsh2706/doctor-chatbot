from config.db_config import get_db_connection

def get_doctor_by_name(name):
    print(f"--- DATABASE DEBUG: Searching for doctor: '{name}' ---")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, specialty FROM doctors WHERE LOWER(name) = LOWER(%s)",
        (name,)
    )
    result = cursor.fetchone()
    print(f"--- DATABASE DEBUG: Result found, get_doctor_by_name: {result} ---")
    cursor.close()
    conn.close()
    return result

def get_doctors_by_specialty(specialty):
    print(f"--- DATABASE DEBUG: Searching for speciality: '{specialty}' ---")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name FROM doctors WHERE LOWER(specialty) = LOWER(%s)",
        (specialty,)
    )
    result = cursor.fetchall()
    print(f"--- DATABASE DEBUG: Result found, gget_doctors_by_specialty: {result} ---")
    cursor.close()
    conn.close()
    return result

def get_availability(doctor_id):
    print(f"--- DATABASE DEBUG: Searching for doctor_id: '{doctor_id}' ---")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT date, time, is_booked
        FROM availability
        WHERE doctor_id = %s
        ORDER BY date, time
        """,
        (doctor_id,)
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def get_available_slot(doctor_id, date, time):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id
        FROM availability
        WHERE doctor_id = %s
        AND date = %s
        AND time = %s
        AND is_booked = FALSE
        """,
        (doctor_id, date, time)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def get_first_available_slot(doctor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT date, time
        FROM availability
        WHERE doctor_id = %s AND is_booked = FALSE
        ORDER BY date, time
        LIMIT 1
        """,
        (doctor_id,)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def book_slot(availability_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE availability SET is_booked = TRUE WHERE id = %s",
        (availability_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()

def create_appointment(doctor_id, patient_name, date, time):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO appointments (doctor_id, patient_name, date, time)
        VALUES (%s, %s, %s, %s)
        """,
        (doctor_id, patient_name, date, time)
    )
    conn.commit()
    cursor.close()
    conn.close()
