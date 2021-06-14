import django_tables2 as tables

from service_api.models import ReportPeriod
from user_profile.models import Profile, Department, Position


class PivotReportTable(tables.Table):
    last_name_and_initial = tables.Column(
        verbose_name="ПІБ", accessor="last_name_and_initial", order_by="user__last_name")
    department = tables.Column(verbose_name=Department._meta.verbose_name, accessor="department__title")
    position = tables.Column(verbose_name=Position._meta.verbose_name, accessor="position__title")
    total_rate = tables.Column(verbose_name="Загальна кількість балів", empty_values=(), orderable=False)

    def render_department(self, value):
        return value.title()

    def render_position(self, value):
        return value.title()

    def render_total_rate(self, record):
        # TODO: filter by selected report_period on UI
        generic_report = record.user.genericreportdata_set.filter(report_period=ReportPeriod.get_active()).first()
        return generic_report.result if generic_report else "N/A"

    class Meta:
        model = Profile
        template_name = "django_tables2/bootstrap-responsive.html"
        exclude = ("user", "id")
        sequence = ("last_name_and_initial", "department", "position", "total_rate")
