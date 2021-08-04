import logging
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

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
    list_display = ("report_period", "is_active", "annual_workload", "download", "download_faculty", 
                    "download_department")
    ordering = ("report_period",)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_form(self, request, form, change):
        is_active = form.cleaned_data.get("is_active")
        if is_active is True:
            ReportPeriod.objects.update(is_active=False)
        return super().save_form(request, form, change)

    @admin.display(description="звіт універсітету")
    def download(self, obj):
        return mark_safe(f"""
        <a href="{reverse('pivot_report_all', kwargs={'report_period_id': obj.pk})}">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-download" viewBox="0 0 16 16">
                <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/>
            </svg>
        </a>
        """)

    @admin.display(description="звіт за факультетом")
    def download_faculty(self, obj):
        options = [f"""
            <option value='{reverse('pivot_report_by_type', 
                                    kwargs={
                                        'report_period_id': obj.pk, 
                                        'level_type': 'faculty',
                                        "pk": f.pk,
                                    })}'>{f}</option>""" for f in Faculty.objects.all()]
        return mark_safe(f"""
            <select onChange="window.location.href=this.value" style="width: 150px;">
                <option>-</option>
                {"".join(options)}
            </select>
        """)

    @admin.display(description="звіт за кафедрою")
    def download_department(self, obj):
        options = [f"""
            <option value='{reverse('pivot_report_by_type',
                                    kwargs={
                                        'report_period_id': obj.pk,
                                        'level_type': 'department',
                                        "pk": f.pk,
                                    })}'>{f}</option>""" for f in Department.objects.all()]
        return mark_safe(f"""
                    <select onChange="window.location.href=this.value" style="width: 150px;">
                        <option>-</option>
                        {"".join(options)}
                    </select>
                """)


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
