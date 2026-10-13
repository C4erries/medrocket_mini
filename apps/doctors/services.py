from dataclasses import dataclass

from doctors.models import Doctor


@dataclass(frozen=True, slots=True)
class DoctorCreateDTO:
    first_name: str
    last_name: str
    specialization: str
    is_active: bool = True

def doctor_create(*, dto: DoctorCreateDTO) -> Doctor:
    doctor = Doctor(
        first_name=dto.first_name.strip(),
        last_name=dto.last_name.strip(),
        specialization=dto.specialization.strip(),
        is_active=dto.is_active,
    )

    doctor.full_clean()
    doctor.save()


    return doctor
