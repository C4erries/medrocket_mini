from django.db import models
from doctors.models import Doctor
from patients.models import Patient


class AppointmentStatus(models.TextChoices):
    """Статусы жизненного цикла записи к врачу."""
    SCHEDULED = "scheduled",  "Запланирован"
    COMPLETED = "completed", "Завершен"
    CANCELED = "canceled", "Отменен"


class Appointment(models.Model):
    """Запись пациента на приём к врачу."""

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Врач",
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name="appointments",
        verbose_name="Пациент",
    )
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.SCHEDULED,
        verbose_name="Статус записи",
    )
    start_time = models.DateTimeField(verbose_name="Время начала приёма")
    end_time = models.DateTimeField(verbose_name="Время окончания приёма")

    notes = models.TextField(blank=True, default="", verbose_name="Примечания")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        db_table = "appointments"
        verbose_name = "Запись на приём"
        verbose_name_plural = "Записи на приём"
        ordering = ["-start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "start_time"],
                condition=~models.Q(status=AppointmentStatus.CANCELED),
                name="unique_active_appointment_per_doctor_slot",
            )
        ]

    def __str__(self) -> str:
        return f"""Appointment(id={self.pk}, status={self.status},
    time={self.start_time.isoformat()})"""
