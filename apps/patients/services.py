from dataclasses import dataclass

from patients.models import Patient


@dataclass(frozen=True, slots=True)
class PatientCreateDTO:
    first_name: str
    last_name: str
    email: str
    phone: str

def patient_create(*, dto: PatientCreateDTO) -> Patient:
    patient = Patient(
        first_name = dto.first_name,
        last_name = dto.last_name,
        email = dto.email,
        phone = dto.phone,
    )

    patient.full_clean()
    patient.save()

    return patient
