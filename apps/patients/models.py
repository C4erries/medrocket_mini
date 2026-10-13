

from django.db import models


class Patient(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(unique=True, verbose_name="Почта")
    phone = models.CharField(max_length=20, verbose_name="Номер телефона")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "patient"
        verbose_name_plural = "patients"
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"Patient id={self.pk}"

