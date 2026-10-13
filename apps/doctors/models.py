from django.db import models


class Doctor(models.Model):
    """Модель врача в клинике."""

    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    specialization = models.CharField(max_length=100, verbose_name="Специализация")
    is_active = models.BooleanField(
        default=True,
        verbose_name="Принимает пациентов",
        help_text="Флаг активности врача для записи",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")


    class Meta:
        db_table = "doctors"
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(
                fields=["specialization", "is_active"],
                name = "idx_doctor_spec_active",
            ),
        ]

    def __str__(self) -> str:
        return f"Doctor id={self.pk} spec={self.specialization}"
