import re
from pydantic import BaseModel, Field, EmailStr, field_validator


# ----------------------------------------
# 1. Base Models for Dates (Already Present)
# ----------------------------------------
class DateTimeModel(BaseModel):
    date: str = Field(description="Date format 'DD-MM-YYYY HH:MM'", pattern=r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$')

    @field_validator("date")
    def check_format_date(cls, v):
        if not re.match(r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$', v):
            raise ValueError("The date should be in format 'DD-MM-YYYY HH:MM'")
        return v


class DateModel(BaseModel):
    date: str = Field(description="Date format 'DD-MM-YYYY'", pattern=r'^\d{2}-\d{2}-\d{4}$')

    @field_validator("date")
    def check_format_date(cls, v):
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', v):
            raise ValueError("The date must be in the format 'DD-MM-YYYY'")
        return v


class IdentificationNumberModel(BaseModel):
    id: int = Field(description="Identification number (positive integer)")

    @field_validator("id")
    def check_format_id(cls, v):
        if v <= 0:
            raise ValueError("The ID number should be a positive integer")
        return v


# ------------------------------------------------
# 2. Doctor Availability Model (doctor_availability.csv)
# ------------------------------------------------
class DoctorAvailabilityModel(BaseModel):
    date_availability: str = Field(pattern=r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$')
    specialization: str
    doctor_name: str
    is_available: bool
    id_patient: int | None = None

    @field_validator("date_availability")
    def validate_date(cls, v):
        if not re.match(r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$', v):
            raise ValueError("date_availability must be in format DD-MM-YYYY HH:MM")
        return v

    @field_validator("is_available")
    def validate_bool(cls, v):
        if isinstance(v, str):
            v_lower = v.lower()
            if v_lower in ["yes", "true", "1", "ture"]:  # Note: "ture" is a typo in the CSV
                return True
            elif v_lower in ["no", "false", "0"]:
                return False
            else:
                raise ValueError(f"Invalid boolean value: {v}")
        return bool(v)


# ------------------------------------------------
# 3. FAQ Model (faqs.csv)
# ------------------------------------------------
class FAQModel(BaseModel):
    question: str
    réponse: str
    catégorie: str
    langue: str

    @field_validator("langue")
    def validate_lang(cls, v):
        if v.lower() not in ["fr", "ar", "en"]:
            raise ValueError("langue must be FR, AR or EN")
        return v.lower()


# ------------------------------------------------
# 4. Doctor Model (médecins.csv)
# ------------------------------------------------
class DoctorModel(BaseModel):
    ID: int
    nom: str
    specialite: str
    qualification: str
    années_d_experience: int = Field(alias="années d'expérience")
    disponibilite: str = Field(alias="disponibilité par jour et heure")

    @field_validator("années_d_experience")
    def validate_experience(cls, v):
        if int(v) < 0:
            raise ValueError("Experience must be >= 0")
        return int(v)


# ------------------------------------------------
# 5. Patient Model (patients.csv)
# ------------------------------------------------
class PatientModel(BaseModel):
    ID: int
    nom: str
    email: EmailStr
    telephone: str
    date_naissance: str
    sexe: str
    addresse: str

    @field_validator("telephone")
    def validate_phone(cls, v):
        if not re.match(r'^[0-9]{8,15}$', v):
            raise ValueError("Phone number must contain 8-15 digits")
        return v

    @field_validator("date_naissance")
    def validate_birthdate(cls, v):
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', v):
            raise ValueError("date_naissance must be DD-MM-YYYY")
        return v


# ------------------------------------------------
# 6. Appointment Model (rendez_vous.csv)
# ------------------------------------------------
class AppointmentModel(BaseModel):
    patient_id: int
    medecin_id: int
    date_rendez_vous: str = Field(alias="date rendez vous")
    heure_rendez_vous: str = Field(alias="heure rendez-vous")
    service: str

    @field_validator("date_rendez_vous")
    def validate_date(cls, v):
        if not re.match(r'^\d{2}-\d{2}-\d{4}$', v):
            raise ValueError("Appointment date must be DD-MM-YYYY")
        return v

    @field_validator("heure_rendez_vous")
    def validate_time(cls, v):
        if not re.match(r'^\d{2}:\d{2}$', v):
            raise ValueError("Time must be HH:MM")
        return v
