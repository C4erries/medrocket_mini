from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime
from typing import cast

from django.core.cache import cache

from appointments.models import Appointment, AppointmentStatus
from core.decorators import measure_and_protect
from core.export import SafeBatchProcessor, chunked_iterable

_NOT_FOUND_SENTINEL = object()

@dataclass(frozen=True, slots=True)
class AppointmentCreateDTO:
    doctor_id: int
    patient_id: int
    start_time: datetime
    end_time: datetime

@measure_and_protect("create_appointment", max_duration_seconds=1.5)
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


def appointment_get(appointment_id: int) -> Appointment | None:
    return Appointment.objects.filter(id=appointment_id).first()

def appointment_notify(appointment: Appointment) -> None:
    pass

def export_appointments_to_csv_rows(
    appointments: Iterable[Appointment],
    chunk_size: int = 100
    ) -> Iterator[list[str]]:
    with SafeBatchProcessor("appointments_csv") as proc:
        csv_strings = []
        for appts in chunked_iterable(appointments, chunk_size):
            for appt in appts:
                csv_strings.append(str(appt))
                proc.track_item()
            yield csv_strings
            csv_strings = []

def appointment_get_cached(appointment_id: int) -> Appointment | None:
    cache_key = f"appointment:{appointment_id}"

    cached_appt = cache.get(cache_key, _NOT_FOUND_SENTINEL)
    if cached_appt is not _NOT_FOUND_SENTINEL:
        return cast(Appointment | None, cached_appt)

    appt = appointment_get(appointment_id)

    timeout = 600 if appt is not None else 30
    cache.set(cache_key, appt, timeout=timeout)

    return appt

def appointment_cancel(appointment_id: int) -> Appointment | None:
    appt = appointment_get_cached(appointment_id)
    if appt is None:
        return None

    if appt.status == AppointmentStatus.CANCELED:
        raise ValueError("Appointment is already canceled")

    appt.status = AppointmentStatus.CANCELED

    appt.save(update_fields=["status", "updated_at"])
    cache.delete(f"appointment:{appointment_id}") # или лучше appt.id какой нибудь

    return appt
