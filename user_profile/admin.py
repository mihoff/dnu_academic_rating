import logging

from django.contrib import admin
from django.db.models import Q

from user_profile.models import Profile, Position, Department, Faculty

logger = logging.getLogger(__name__)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user_", "position_", "department_", "faculty_", "last_login")
    list_per_page = 50
    search_fields = ("user__last_name", "user__first_name", "user__email")
    ordering = ("-user__last_login",)

    @admin.display(description="Користувач", ordering="user__last_name")
    def user_(self, obj):
        return f"{obj.user.last_name} {obj.user.first_name} "

    @admin.display(description=Position._meta.verbose_name, ordering="position")
    def position_(self, obj):
        return obj.position

    @admin.display(description=Department._meta.verbose_name, ordering="department")
    def department_(self, obj):
        return obj.department

    @admin.display(description=Faculty._meta.verbose_name, empty_value="-", ordering="department__faculty")
    def faculty_(self, obj):
        return obj.department.faculty if obj.department else "-"

    @admin.display(description="Дата останнього входу", ordering="user__last_login")
    def last_login(self, obj):
        return obj.user.last_login

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            if request.user.profile.position.cumulative_calculation == Position.BY_DEPARTMENT:
                qs = qs.filter(
                    Q(
                        Q(department=request.user.profile.department) |
                        Q(position__isnull=True) |
                        Q(department__isnull=True)
                    ) & Q(user__is_superuser=False)
                )
            elif request.user.profile.position.cumulative_calculation == Position.BY_FACULTY:
                qs = qs.filter(
                    Q(
                        Q(department__faculty=request.user.profile.department.faculty) |
                        Q(position__isnull=True) |
                        Q(department__isnull=True)
                    ) & Q(user__is_superuser=False)
                )
        except Exception as e:
            logging.info(f"ProfileAdmin :: {e}")

        return qs

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["user"].label = "Користувач"
        form.base_fields["department"].label = Department._meta.verbose_name
        form.base_fields["position"].label = Position._meta.verbose_name
        return form

    def save_model(self, request, obj, form, change):
        if obj.position.cumulative_calculation is not None:
            obj.user.is_staff = True
            obj.user.save()
        super().save_model(request, obj, form, change)


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
