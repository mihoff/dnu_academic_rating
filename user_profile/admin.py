import logging

from django.contrib import admin

from django.utils.translation import gettext as _
from user_profile.models import Profile, Position, Department, Faculty

logger = logging.getLogger(__name__)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user_", "position_", "department_", "faculty_", "last_login", "date_joined")
    list_per_page = 50
    search_fields = ("user__last_name", "user__first_name", "user__email")

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

    @admin.display(description="Дата приєднання")
    def date_joined(self, obj):
        return obj.user.date_joined

    @admin.display(description="Дата останнього входу")
    def last_login(self, obj):
        return obj.user.last_login

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            if request.user.profile.position.cumulative_calculation == Position.BY_DEPARTMENT:
                qs = qs.filter(department=request.user.profile.department)
            elif self.request.user.profile.position.cumulative_calculation == Position.BY_FACULTY:
                qs = qs.filter(department__faculty=request.user.profile.department.faculty)
        except Exception as e:
            logging.error(f"ProfileAdmin :: {e}")

        return qs


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "people_cnt")

    @admin.display(description="Кількість працівників", empty_value="0")
    def people_cnt(self, obj):
        return obj.profile_set.count()


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("__str__", "faculty", "people_cnt")

    @admin.display(description="Кількість працівників", empty_value="0")
    def people_cnt(self, obj):
        return obj.profile_set.count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            if request.user.profile.position.cumulative_calculation == Position.BY_DEPARTMENT:
                qs = qs.filter(pk=request.user.profile.department.pk)
            elif self.request.user.profile.position.cumulative_calculation == Position.BY_FACULTY:
                qs = qs.filter(faculty=request.user.profile.department.faculty)
        except Exception as e:
            logging.error(f"ProfileAdmin :: {e}")

        return qs


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("__str__", "people_cnt", "dep_cnt")

    @admin.display(description="Кількість працівників", empty_value="0")
    def people_cnt(self, obj):
        return Profile.objects.filter(department__in=obj.department_set.all()).count()

    @admin.display(description="Кількість кафедр", empty_value="0")
    def dep_cnt(self, obj):
        return obj.department_set.count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            if request.user.profile.position.cumulative_calculation == Position.BY_DEPARTMENT:
                qs = qs.filter(department=request.user.profile.department)
            elif self.request.user.profile.position.cumulative_calculation == Position.BY_FACULTY:
                qs = qs.filter(pk=request.user.profile.department.faculty.pk)
        except Exception as e:
            logging.error(f"ProfileAdmin :: {e}")

        return qs
