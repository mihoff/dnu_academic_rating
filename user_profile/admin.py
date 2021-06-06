from django.contrib import admin

from django.utils.translation import gettext as _
from user_profile.models import Profile, Position, Department, Faculty


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user_", "position_", "department_")

    @admin.display(description=_("User"))
    def user_(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    @admin.display(description=Position._meta.verbose_name)
    def position_(self, obj):
        return f"{obj.position.title if obj.position else '-'}"

    @admin.display(description=Department._meta.verbose_name)
    def department_(self, obj):
        return f"{obj.department.title if obj.department else '-'}"




@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    ...


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    ...


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    ...
