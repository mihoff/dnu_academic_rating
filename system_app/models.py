from django.db import models


class Documents(models.Model):
    file = models.FileField(
        verbose_name="Файл", upload_to="uploads/service_app/documents", default=None, null=True, max_length=256)
    name = models.CharField(
        verbose_name="Назва файлу", max_length=100, help_text="Якщо не вказано, буде викорастано назву із файлу",
        null=True, blank=True)
    description = models.TextField(verbose_name="Опис файлу", null=True, blank=True)
    visible = models.BooleanField(verbose_name="Доступно користувачам", default=True)

    class Meta:
        verbose_name = "документ"
        verbose_name_plural = "Документи"

    def __str__(self):
        return self.name
