from django.contrib import admin

from service_api.models import ReportPeriod, GenericReportData
from user_profile.models import Department, Faculty


@admin.register(ReportPeriod)
class ReportPeriodAdmin(admin.ModelAdmin):
    list_display = ("report_period", "is_active")
    ordering = ("report_period",)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(GenericReportData)
class GenericReportDataAdmin(admin.ModelAdmin):
    list_display = ("user_", "department_", "faculty_", "report_period", "result", "is_closed")
    ordering = ("user__profile__department__faculty", "user__profile__department")

    @admin.display(description="Користувач", ordering="user")
    def user_(self, obj):
        return obj.user.profile.last_name_and_initial

    @admin.display(description=Department._meta.verbose_name, ordering="user__profile__department")
    def department_(self, obj):
        return obj.user.profile.department

    @admin.display(description=Faculty._meta.verbose_name, ordering="user__profile__department__faculty")
    def faculty_(self, obj):
        return obj.user.profile.department.faculty
