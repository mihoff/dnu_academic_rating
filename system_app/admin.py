import json

from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.apps import AuthConfig as UserAuthConfig
from django.contrib.auth.models import User
from django.core import validators
from django.db.models import Q

from system_app.models import Documents
from user_profile.models import Department, Position, Faculty


class UserAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name_", "email", "position_", "department_", "faculty_")
    list_filter = ("is_staff", "is_superuser")
    fields = ("email", "first_name", "last_name", "groups", "user_permissions")
    search_fields = (
        'first_name', 'last_name', 'email', "profile__position__title", "profile__department__title",
        "profile__department__faculty__title")

    @admin.display(description="Ім'я По-батькові", ordering="first_name")
    def first_name_(self, obj):
        return obj.first_name

    @admin.display(description=Position._meta.verbose_name, ordering="profile__position")
    def position_(self, obj):
        return getattr(obj.profile, "position", "-")

    @admin.display(description=Department._meta.verbose_name, ordering="profile__department")
    def department_(self, obj):
        return getattr(obj.profile, "department", "-")

    @admin.display(description=Faculty._meta.verbose_name, empty_value="-", ordering="profile__department__faculty")
    def faculty_(self, obj):
        return getattr(obj.profile, "department", None) and obj.profile.department.faculty or "-"

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["email"].required = True
        form.base_fields["first_name"].required = True
        form.base_fields["first_name"].label = "Ім'я По-батькові"
        form.base_fields["first_name"].validators.append(
            validators.RegexValidator(
                r"(\w+\s\w+){1}", message="Невірний формат: Ім'я та По-батькові повинні бути вказані через пробіл"))
        form.base_fields["last_name"].required = True
        return form

    def get_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_fields(request, obj)
        return ["email", "first_name", "last_name"]

    def save_form(self, request, form, change):
        user = super().save_form(request, form, change)
        user.email = user.email.lower().strip()
        user.username = user.email
        user.set_unusable_password()
        return user

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            try:
                if request.user.profile.position.cumulative_calculation == Position.BY_DEPARTMENT:
                    qs = qs.filter(
                        Q(
                            Q(profile__department=request.user.profile.department) |
                            Q(profile__position__isnull=True) |
                            Q(profile__department__isnull=True)
                        ) & Q(is_superuser=False)
                    )
                elif request.user.profile.position.cumulative_calculation == Position.BY_FACULTY:
                    qs = qs.filter(
                        Q(
                            Q(profile__department__faculty=request.user.profile.department.faculty) |
                            Q(profile__position__isnull=True) |
                            Q(profile__department__isnull=True)
                        ) & Q(is_superuser=False)
                    )
            except:
                pass

        return qs


UserAuthConfig.verbose_name = "1. Користувачі"

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "visible")

    def save_model(self, request, obj, form, change):
        if obj.name is None:
            obj.name = obj.file.name.replace(Documents.file.field.upload_to + "/", "").split(".")[0]
        super().save_model(request, obj, form, change)


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    date_hierarchy = "action_time"
    list_filter = ["content_type", "action_flag"]
    search_fields = ["object_repr", "change_message"]
    list_display = ["action_time", "user", "content_type", "action_flag"]

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field)
        if obj:
            obj.change_message = str(json.loads(obj.change_message))
        return obj
