from django.core.management.base import BaseCommand

from service_api.calculations.educational_and_methodical_work_calc import EducationalAndMethodicalWorkCalculation
from service_api.calculations.generic_report_calc import GenericReportCalculation
from service_api.calculations.organizational_and_educational_work_calc import (
    OrganizationalAndEducationalWorkCalculation,
)
from service_api.calculations.scientific_and_innovative_work_calc import ScientificAndInnovativeWorkCalculation
from service_api.models import (
    ReportPeriod,
    REPORT_MODELS,
    EducationalAndMethodicalWork,
    ScientificAndInnovativeWork,
    OrganizationalAndEducationalWork,
)
from user_profile.models import Profile

MODEL_CALC_MAP = {
    EducationalAndMethodicalWork.__name__.lower(): EducationalAndMethodicalWorkCalculation,
    ScientificAndInnovativeWork.__name__.lower(): ScientificAndInnovativeWorkCalculation,
    OrganizationalAndEducationalWork.__name__.lower(): OrganizationalAndEducationalWorkCalculation,
}


class Command(BaseCommand):
    help = "Calculate all reports for all users"

    def handle(self, *args, **options):
        report_period = ReportPeriod.objects.get(is_active=True)
        for profile in Profile.objects.filter(department__isnull=False):
            self.stdout.write(f"Calculating for {profile.user.username}...", ending=" ")
            generic_reports = profile.user.genericreportdata_set.filter(report_period=report_period)
            if not generic_reports:
                self.stdout.write("No reports found", style_func=self.style.ERROR)
                continue
            generic_report = generic_reports.first()
            for report_model in REPORT_MODELS:
                report = getattr(generic_report, report_model.__name__.lower(), None)
                if not report:
                    self.stdout.write(
                        f"No report {report_model.__name__.lower()} found", style_func=self.style.ERROR, ending=" "
                    )
                    report = report_model.objects.create(generic_report_data=generic_report)

                result = MODEL_CALC_MAP[report_model.__name__.lower()](report).get_result()
                report.result = result
                report.adjusted_result = report_model.raw_calculation(result, generic_report)
                report.save()

            calc_obj = GenericReportCalculation(generic_report)
            generic_report.result = calc_obj.get_result()
            generic_report.save()
            self.stdout.write("finished")
