import logging

from django.contrib import admin

from service_api.models import (
    ReportPeriod,
    GenericReportData,
    EducationalAndMethodicalWork,
    ScientificAndInnovativeWork,
    OrganizationalAndEducationalWork)
from user_profile.models import Department, Faculty, Position

logger = logging.getLogger(__name__)


class BaseReportAdmin(admin.ModelAdmin):
    list_display = ("user_", "department_", "faculty_", "report_period", "result", "is_closed_",
                    "created_at", "updated_at")

    def get_ordering(self, request):
        one, two = "user__profile__department__faculty", "user__profile__department"
        if hasattr(self.model, "generic_report_data"):
            one = f"generic_report_data__{one}"
            two = f"generic_report_data__{two}"
        return one, two

    @admin.display(description="Користувач", ordering="user", empty_value="")
    def user_(self, obj):
        _obj = getattr(obj, "generic_report_data", obj)
        if _obj is not None:
            return _obj.user.profile.last_name_and_initial

    @admin.display(description=Department._meta.verbose_name, ordering="user__profile__department")
    def department_(self, obj):
        _obj = getattr(obj, "generic_report_data", obj)
        if _obj is not None:
            return _obj.user.profile.department

    @admin.display(description=Faculty._meta.verbose_name, ordering="user__profile__department__faculty")
    def faculty_(self, obj):
        _obj = getattr(obj, "generic_report_data", obj)
        if _obj is not None:
            return _obj.user.profile.department.faculty

    @admin.display(description=GenericReportData.is_closed.field.verbose_name, boolean=True)
    def is_closed_(self, obj):
        _obj = getattr(obj, "generic_report_data", obj)
        if _obj is not None:
            return _obj.is_closed


@admin.register(ReportPeriod)
class ReportPeriodAdmin(admin.ModelAdmin):
    list_display = ("report_period", "is_active", "annual_workload")
    ordering = ("report_period",)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_form(self, request, form, change):
        is_active = form.cleaned_data.get("is_active")
        if is_active is True:
            ReportPeriod.objects.update(is_active=False)
        return super().save_form(request, form, change)


@admin.register(GenericReportData)
class GenericReportDataAdmin(BaseReportAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            if request.user.profile.position.cumulative_calculation == Position.BY_DEPARTMENT:
                qs = qs.filter(user__profile__department=request.user.profile.department)
            elif self.request.user.profile.position.cumulative_calculation == Position.BY_FACULTY:
                qs = qs.filter(user__profile__department__faculty=request.user.profile.department.faculty)
        except Exception as e:
            logging.error(f"GenericReportDataAdmin :: {e}")

        return qs


@admin.register(EducationalAndMethodicalWork)
class EducationalAndMethodicalWorkAdmin(BaseReportAdmin):
    ...


@admin.register(ScientificAndInnovativeWork)
class ScientificAndInnovativeWorkAdmin(BaseReportAdmin):
    ...


@admin.register(OrganizationalAndEducationalWork)
class OrganizationalAndEducationalWorkAdmin(BaseReportAdmin):
    ...
