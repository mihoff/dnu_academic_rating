from django.db import models
from microsoft_auth.models import User


class Feedback(models.Model):
    name = models.CharField(verbose_name="Ім'я", max_length=100, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    feedback = models.TextField(verbose_name="Відгук")

    seen = models.BooleanField(verbose_name="Опрацьовано?", default=False)
    comment = models.TextField(verbose_name="Коментар", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Додано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Останнє редагування")

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
