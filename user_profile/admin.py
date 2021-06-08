from django.contrib import admin

from django.utils.translation import gettext as _
from user_profile.models import Profile, Position, Department, Faculty


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user_", "position_", "department_", "faculty_")
    list_per_page = 50

    @admin.display(description=_("User"), ordering="user")
    def user_(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    @admin.display(description=Position._meta.verbose_name, ordering="position")
    def position_(self, obj):
        return f"{obj.position if obj.position else '-'}"

    @admin.display(description=Department._meta.verbose_name, ordering="department")
    def department_(self, obj):
        return f"{obj.department if obj.department else '-'}"

    @admin.display(description=Faculty._meta.verbose_name, empty_value="-", ordering="department__faculty")
    def faculty_(self, obj):
        return obj.department.faculty if obj.department else "-"


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "people_cnt")

    @admin.display(description="Кількість працівників", empty_value="0")
    def people_cnt(self, obj):
        return obj.profile_set.count()


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("__str__", "people_cnt")

    @admin.display(description="Кількість працівників", empty_value="0")
    def people_cnt(self, obj):
        return obj.profile_set.count()


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("__str__", "people_cnt", "dep_cnt")

    @admin.display(description="Кількість працівників", empty_value="0")
    def people_cnt(self, obj):
        return Profile.objects.filter(department__in=obj.department_set.all()).count()

    @admin.display(description="Кількість кафедр", empty_value="0")
    def dep_cnt(self, obj):
        return obj.department_set.count()
