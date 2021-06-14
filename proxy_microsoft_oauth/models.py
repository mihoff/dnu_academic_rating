from django.db import models


class AllowedMicrosoftAccount(models.Model):
    tail = models.CharField(max_length=256, help_text="To be checked literally with an income User email", default="")

    def __str__(self):
        return f"*{self.tail}"
