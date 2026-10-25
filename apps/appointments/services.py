from dataclasses import dataclass
from datetime import datetime

from appointments.models import Appointment, AppointmentStatus


@dataclass(frozen=True, slots=True)
class AppointmentCreateDTO:
    doctor_id: int
    patient_id: int
    start_time: datetime
    end_time: datetime


def appointment_create(
    dto: AppointmentCreateDTO,
    /,
    *,
    send_notification: bool = True,
    symptoms: list[str] | None = None
    ) -> Appointment:
    if symptoms is None:
        symptoms = []

    if dto.start_time >= dto.end_time:
        raise ValueError("start_time must be before end_time")

    appointment = Appointment(
        doctor_id = dto.doctor_id,
        patient_id = dto.patient_id,
        status = AppointmentStatus.SCHEDULED,
        notes = ";\n".join(list(symptoms)),
        start_time = dto.start_time,
        end_time = dto.end_time,
    )

    appointment.full_clean()
    appointment.save()

    if send_notification:
        appointment_notify(appointment)

    return appointment

def appointment_notify(appointment: Appointment) -> None:
    pass
