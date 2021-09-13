from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.apps import AuthConfig as UserAuthConfig
from django.core import validators

from system_app.models import Documents
from user_profile.models import Department, Position, Faculty


class UserAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name_", "email", "position_", "department_", "faculty_")
    list_filter = ("is_staff", "is_superuser")
    fields = ("email", "first_name", "last_name", "groups", "user_permissions")
    search_fields = ('first_name', 'last_name', 'email')

    @admin.display(description="Ім'я По-батькові", ordering="first_name")
    def first_name_(self, obj):
        return obj.first_name

    @admin.display(description=Position._meta.verbose_name, ordering="position")
    def position_(self, obj):
        return getattr(obj.profile, "position", "-")

    @admin.display(description=Department._meta.verbose_name, ordering="department")
    def department_(self, obj):
        return getattr(obj.profile, "department", "-")

    @admin.display(description=Faculty._meta.verbose_name, empty_value="-", ordering="department__faculty")
    def faculty_(self, obj):
        return getattr(obj.profile, "department", None) and obj.profile.department.faculty or "-"

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        if not request.user.is_superuser:
            form.base_fields.pop("groups", None)
            form.base_fields.pop("user_permissions", None)
        form.base_fields["email"].required = True
        form.base_fields["first_name"].required = True
        form.base_fields["first_name"].label = "Ім'я По-батькові"
        form.base_fields["first_name"].validators.append(
            validators.RegexValidator(
                r"(\w+\s\w+){1}", message="Невірний формат: Ім'я та По-батькові повинні бути вказані через пробіл"))
        form.base_fields["last_name"].required = True
        return form

    def save_form(self, request, form, change):
        user = super().save_form(request, form, change)
        user.username = user.email
        user.set_unusable_password()
        return user

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            if request.user.profile.position.cumulative_calculation == Position.BY_DEPARTMENT:
                qs = qs.filter(profile__department=request.user.profile.department)
            elif self.request.user.profile.position.cumulative_calculation == Position.BY_FACULTY:
                qs = qs.filter(profile__department__faculty=request.user.profile.department.faculty)
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

