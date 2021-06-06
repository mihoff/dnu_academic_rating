from django.contrib import admin

from service_api.models import ReportPeriod


@admin.register(ReportPeriod)
class ReportPeriodAdmin(admin.ModelAdmin):
    list_display = ("report_period", "is_active")

    def has_delete_permission(self, request, obj=None):
        return False
