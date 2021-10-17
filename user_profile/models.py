from django.contrib.auth.models import User
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver


class Faculty(models.Model):
    title = models.CharField(max_length=256, verbose_name="назва")

    class Meta:
        verbose_name = "Факультет"
        verbose_name_plural = "Факультети"
        constraints = [UniqueConstraint(fields=["title"], name="unique_faculty_title")]

    def __str__(self):
        return self.title.title()

    def clean(self):
        self.title = self.title.lower()
        super().clean()


class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, verbose_name="факультет", blank=True, null=True)
    title = models.CharField(max_length=256, verbose_name="назва")

    def __str__(self):
        return self.title.title()

    def clean(self):
        self.title = self.title.lower()
        super().clean()

    class Meta:
        verbose_name = "Кафедра"
        verbose_name_plural = "Кафедри"
        constraints = [UniqueConstraint(fields=["title", "faculty"], name="unique_department_faculty_title")]
        ordering = ["title"]


class Position(models.Model):
    BY_DEPARTMENT = "department"
    BY_FACULTY = "faculty"
    CUMULATIVE_CALCULATION_CHOICES = (
        (BY_DEPARTMENT, "По Кафедрі"),
        (BY_FACULTY, "По Факультету")
    )

    title = models.CharField(max_length=256, verbose_name="назва")
    cumulative_calculation = models.CharField(
        max_length=20, choices=CUMULATIVE_CALCULATION_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.title.title()

    def clean(self):
        self.title = self.title.lower()
        super().clean()

    class Meta:
        verbose_name = "Посада"
        verbose_name_plural = "Посади"
        constraints = [UniqueConstraint(fields=["title"], name="unique_position_title")]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def last_name_and_initial(self):
        try:
            res = f"{self.user.last_name} {'. '.join([i[0] for i in self.user.first_name.split(' ')])}."
        except IndexError:
            res = self.user.email
        return res

    def __str__(self):
        try:
            return f"{self.user.first_name} {self.user.last_name} ({self.position}/{self.department})"
        except AttributeError:
            return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        verbose_name = "Профіль користувача"
        verbose_name_plural = "Профілі користувачів"
        constraints = [UniqueConstraint(fields=["user", "department", "position"], name="unique_profile")]
        ordering = ["department__title", "department__faculty__title"]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


def user_str(self):
    try:
        return f"{self.last_name} {self.first_name} ({self.profile.position or '-'}/{self.profile.department or '-'})"
    except AttributeError:
        return f"{self.last_name} {self.first_name}"


User.add_to_class("__str__", user_str)
