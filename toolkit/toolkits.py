import pandas as pd
from langchain_core.tools import tool
from data_models.models import (
    DateModel,
    DateTimeModel,
    IdentificationNumberModel,
    PatientModel
)


DATA_PATH = "data/"   # important ! adapt path if needed


# -------------------------------------------------------
# 1) CHECK AVAILABILITY BY DOCTOR
# -------------------------------------------------------
@tool
def check_availability_by_doctor(desired_date: str, doctor_name: str):
    """
    Return all available time slots for a doctor in a given day.
    Date format: DD-MM-YYYY HH:MM (for specific time) or DD-MM-YYYY (for all day slots)
    """
    # Check if date includes time
    if " " in desired_date:
        # Specific time check
        date_model = DateTimeModel(date=desired_date)
        df = pd.read_csv(DATA_PATH + "doctor_availability.csv")
        
        # Find exact time slot
        slot = df[
            (df["date_availability"] == date_model.date) &
            (df["doctor_name"].str.lower() == doctor_name.lower())
        ]
        
        if len(slot) == 0:
            return f"No time slot found for Dr {doctor_name} at {date_model.date}"
        
        is_available = slot.iloc[0]["is_available"]
        if is_available:
            return f"Dr {doctor_name} is available at {date_model.date}"
        else:
            return f"Dr {doctor_name} is NOT available at {date_model.date} (already booked)"
    else:
        # Daily availability check - show all time slots
        date_model = DateModel(date=desired_date)
        df = pd.read_csv(DATA_PATH + "doctor_availability.csv")
        
        # Filter by date (partial match) + doctor
        day_rows = df[
            (df["date_availability"].str.startswith(date_model.date)) &
            (df["doctor_name"].str.lower() == doctor_name.lower())
        ]
        
        if len(day_rows) == 0:
            return f"No availability found for Dr {doctor_name} on {date_model.date}"
        
        # Separate available and booked slots
        available_slots = day_rows[day_rows["is_available"] == True]
        booked_slots = day_rows[day_rows["is_available"] == False]
        
        if len(available_slots) == 0:
            return f"Dr {doctor_name} has no available slots on {date_model.date}. All slots are booked."
        
        # Format output
        output = f"Available time slots for Dr {doctor_name} on {date_model.date}:\n"
        for _, slot in available_slots.iterrows():
            time = slot["date_availability"].split(" ")[1] if " " in slot["date_availability"] else "Unknown time"
            output += f"- {time}\n"
        
        if len(booked_slots) > 0:
            output += f"\nBooked slots: {len(booked_slots)} time slots are already taken."
        
        return output



# -------------------------------------------------------
# 2) CHECK AVAILABILITY BY SPECIALIZATION
# -------------------------------------------------------
@tool
def check_availability_by_specialization(desired_date: str, specialization: str):
    """
    Check which doctors of a specialization are available on a given date.
    Date format: DD-MM-YYYY (shows all time slots for the day)
    """
    date_model = DateModel(date=desired_date)
    df = pd.read_csv(DATA_PATH + "doctor_availability.csv")

    # Filter by date (partial match) + specialization + available
    rows = df[
        (df["date_availability"].str.startswith(date_model.date)) &
        (df["specialization"].str.lower() == specialization.lower()) &
        (df["is_available"] == True)
    ]

    if len(rows) == 0:
        return f"No doctors available in {specialization} on {date_model.date}"

    # Group by doctor and collect available time slots
    doctors_data = {}
    for _, row in rows.iterrows():
        doctor_name = row["doctor_name"]
        time_slot = row["date_availability"].split(" ")[1] if " " in row["date_availability"] else "Unknown"
        
        if doctor_name not in doctors_data:
            doctors_data[doctor_name] = []
        doctors_data[doctor_name].append(time_slot)
    
    # Format output
    output = f"Available {specialization} doctors for {date_model.date}:\n\n"
    for doctor_name, time_slots in doctors_data.items():
        output += f"Dr {doctor_name}:\n"
        for time_slot in sorted(time_slots):
            output += f"  - {time_slot}\n"
        output += f"  Total available slots: {len(time_slots)}\n\n"
    
    return output


# -------------------------------------------------------
# 3) SET APPOINTMENT
# -------------------------------------------------------
@tool
def set_appointment(desired_date: str, id_number: int, doctor_name: str):
    """
    Book an appointment: 
    - add appointment to rendez_vous.csv
    - mark doctor as unavailable in doctor_availability.csv
    Date format: DD-MM-YYYY HH:MM
    ID number: integer (7-8 digits)
    """
    date_model = DateTimeModel(date=desired_date)
    id_model = IdentificationNumberModel(id=id_number)
    
    df = pd.read_csv(DATA_PATH + "doctor_availability.csv")

    # check availability for exact time slot
    case = df[
        (df["date_availability"] == date_model.date) &
        (df["doctor_name"].str.lower() == doctor_name.lower()) &
        (df["is_available"] == True)
    ]

    if len(case) == 0:
        # Check if slot exists but is booked
        slot_exists = df[
            (df["date_availability"] == date_model.date) &
            (df["doctor_name"].str.lower() == doctor_name.lower())
        ]
        if len(slot_exists) > 0:
            return f"Time slot {date_model.date} for Dr {doctor_name} is already booked."
        else:
            return f"No time slot found for Dr {doctor_name} at {date_model.date}."

    # book appointment in rendez_vous.csv
    df_app = pd.read_csv(DATA_PATH + "rendez_vous.csv")

    new_row = {
        "patient_id": id_model.id,
        "medecin_id": case.iloc[0].get("id_patient", 0),
        "date rendez vous": date_model.date.split(" ")[0],  # Date part only
        "heure rendez-vous": date_model.date.split(" ")[1],  # Time part
        "service": case.iloc[0]["specialization"]
    }

    df_app.loc[len(df_app)] = new_row
    df_app.to_csv(DATA_PATH + "rendez_vous.csv", index=False)

    # update availability for exact time slot
    df.loc[
        (df["date_availability"] == date_model.date) &
        (df["doctor_name"].str.lower() == doctor_name.lower()),
        ["is_available", "id_patient"]
    ] = [False, id_model.id]

    df.to_csv(DATA_PATH + "doctor_availability.csv", index=False)

    return f"Appointment successfully created for {date_model.date}."


# -------------------------------------------------------
# 4) CANCEL APPOINTMENT
# -------------------------------------------------------
@tool
def cancel_appointment(date: str, id_number: int, doctor_name: str):
    """
    Cancel appointment:
    - remove from rendez_vous.csv
    - re-enable availability
    Date format: DD-MM-YYYY HH:MM
    ID number: integer (7-8 digits)
    """
    date_model = DateTimeModel(date=date)
    id_model = IdentificationNumberModel(id=id_number)
    
    df_app = pd.read_csv(DATA_PATH + "rendez_vous.csv")
    df_avl = pd.read_csv(DATA_PATH + "doctor_availability.csv")

    day = date_model.date.split(" ")[0]
    time = date_model.date.split(" ")[1]

    # Find appointment in rendez_vous.csv
    case = df_app[
        (df_app["patient_id"] == id_model.id) &
        (df_app["date rendez vous"] == day) &
        (df_app["heure rendez-vous"] == time) &
        (df_app["medecin_id"].notna())
    ]

    if len(case) == 0:
        return f"No appointment found for patient {id_model.id} with Dr {doctor_name} at {date_model.date}."

    # remove row
    df_app = df_app.drop(case.index)
    df_app.to_csv(DATA_PATH + "rendez_vous.csv", index=False)

    # re-enable availability for exact time slot
    df_avl.loc[
        (df_avl["date_availability"] == date_model.date) &
        (df_avl["doctor_name"].str.lower() == doctor_name.lower()),
        ["is_available", "id_patient"]
    ] = [True, None]

    df_avl.to_csv(DATA_PATH + "doctor_availability.csv", index=False)

    return f"Appointment successfully cancelled for {date_model.date}."


# -------------------------------------------------------
# 5) RESCHEDULE APPOINTMENT
# -------------------------------------------------------
@tool
def reschedule_appointment(old_date: str, new_date: str, id_number: int, doctor_name: str):
    """
    Reschedule = cancel old + set new
    Date format: DD-MM-YYYY HH:MM
    ID number: integer (7-8 digits)
    """
    cancel_msg = cancel_appointment(old_date, id_number, doctor_name)
    if "successfully" not in cancel_msg.lower():
        return "Cannot reschedule because cancellation failed."

    create_msg = set_appointment(new_date, id_number, doctor_name)
    if "successfully" not in create_msg.lower():
        return "Cannot reschedule because new booking failed."

    return "Appointment successfully rescheduled!"


# -------------------------------------------------------
# 6) PATIENT MANAGEMENT TOOLS
# -------------------------------------------------------

@tool
def create_patient(
    nom: str,
    email: str,
    telephone: str,
    date_naissance: str,
    sexe: str,
    addresse: str
):
    """
    Create a new patient record.
    Date format: DD-MM-YYYY
    Telephone: 8-15 digits
    Sexe: M or F
    """
    # Read existing patients
    df = pd.read_csv(DATA_PATH + "patients.csv")
    
    # Generate new ID (max existing ID + 1)
    new_id = df["ID"].max() + 1 if len(df) > 0 else 1
    
    # Create patient data
    patient_data = {
        "ID": new_id,
        "nom": nom,
        "email": email,
        "telephone": telephone,
        "date_naissance": date_naissance,
        "sexe": sexe,
        "addresse": addresse
    }
    
    # Validate using PatientModel
    try:
        patient = PatientModel(**patient_data)
    except Exception as e:
        return f"Validation error: {str(e)}"
    
    # Add to dataframe
    df.loc[len(df)] = patient_data
    df.to_csv(DATA_PATH + "patients.csv", index=False)
    
    return f"Patient created successfully with ID: {new_id}"


@tool
def get_patient(id_number: int):
    """
    Retrieve patient information by ID.
    ID number: integer (existing patient ID)
    """
    # Validate ID format
    id_model = IdentificationNumberModel(id=id_number)
    
    df = pd.read_csv(DATA_PATH + "patients.csv")
    
    # Find patient
    patient = df[df["ID"] == id_model.id]
    
    if len(patient) == 0:
        return f"No patient found with ID: {id_model.id}"
    
    patient_info = patient.iloc[0]
    
    return (
        f"Patient ID: {patient_info['ID']}\n"
        f"Name: {patient_info['nom']}\n"
        f"Email: {patient_info['email']}\n"
        f"Phone: {patient_info['telephone']}\n"
        f"Birth Date: {patient_info['date_naissance']}\n"
        f"Gender: {patient_info['sexe']}\n"
        f"Address: {patient_info['addresse']}"
    )


@tool
def update_patient(
    id_number: int,
    nom: str = None,
    email: str = None,
    telephone: str = None,
    date_naissance: str = None,
    sexe: str = None,
    addresse: str = None
):
    """
    Update patient information.
    ID number: integer (existing patient ID)
    Provide only the fields you want to update.
    """
    # Validate ID format
    id_model = IdentificationNumberModel(id=id_number)
    
    df = pd.read_csv(DATA_PATH + "patients.csv")
    
    # Find patient
    patient_idx = df[df["ID"] == id_model.id].index
    
    if len(patient_idx) == 0:
        return f"No patient found with ID: {id_model.id}"
    
    idx = patient_idx[0]
    
    # Update only provided fields
    update_data = {}
    if nom is not None:
        update_data["nom"] = nom
    if email is not None:
        update_data["email"] = email
    if telephone is not None:
        update_data["telephone"] = telephone
    if date_naissance is not None:
        update_data["date_naissance"] = date_naissance
    if sexe is not None:
        update_data["sexe"] = sexe
    if addresse is not None:
        update_data["addresse"] = addresse
    
    # Apply updates
    for key, value in update_data.items():
        df.at[idx, key] = value
    
    # Validate the updated record
    try:
        patient_data = df.iloc[idx].to_dict()
        PatientModel(**patient_data)
    except Exception as e:
        return f"Validation error after update: {str(e)}"
    
    df.to_csv(DATA_PATH + "patients.csv", index=False)
    
    return f"Patient ID {id_model.id} updated successfully."


@tool
def check_patient_id(id_number: int):
    """
    Check if a patient ID exists in the system.
    ID number: integer (7-8 digits)
    Returns: True if exists, False otherwise
    """
    # Validate ID format
    id_model = IdentificationNumberModel(id=id_number)
    
    df = pd.read_csv(DATA_PATH + "patients.csv")
    
    exists = id_model.id in df["ID"].values
    
    return f"Patient ID {id_model.id} exists: {exists}"


# -------------------------------------------------------
# 7) GET PATIENT APPOINTMENTS
# -------------------------------------------------------
@tool
def get_patient_appointments(id_number: int):
    """
    Get all appointments for a patient.
    ID number: integer (patient ID)
    Returns: List of appointments with details
    """
    # Validate ID format
    id_model = IdentificationNumberModel(id=id_number)
    
    # Check if patient exists
    df_patients = pd.read_csv(DATA_PATH + "patients.csv")
    if id_model.id not in df_patients["ID"].values:
        return f"No patient found with ID: {id_model.id}"
    
    # Get appointments
    df_appointments = pd.read_csv(DATA_PATH + "rendez_vous.csv")
    patient_appointments = df_appointments[df_appointments["patient_id"] == id_model.id]
    
    if len(patient_appointments) == 0:
        return f"No appointments found for patient ID: {id_model.id}"
    
    # Get doctor names from doctors.csv
    df_doctors = pd.read_csv(DATA_PATH + "doctors.csv")
    
    # Format output
    output = f"Appointments for patient ID {id_model.id}:\n\n"
    for idx, appointment in patient_appointments.iterrows():
        # Get doctor name
        doctor_id = appointment["medecin_id"]
        doctor_info = df_doctors[df_doctors["ID"] == doctor_id]
        doctor_name = doctor_info.iloc[0]["nom"] if len(doctor_info) > 0 else f"Doctor ID {doctor_id}"
        
        output += f"Appointment {idx + 1}:\n"
        output += f"  Doctor: {doctor_name}\n"
        output += f"  Date: {appointment['date rendez vous']}\n"
        output += f"  Time: {appointment['heure rendez-vous']}\n"
        output += f"  Service: {appointment['service']}\n"
        output += f"  Appointment ID: {idx}\n\n"
    
    return output
