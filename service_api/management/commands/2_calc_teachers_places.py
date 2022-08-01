import csv
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q

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
    TeacherResults,
)
from user_profile.models import Profile

MODEL_CALC_MAP = {
    EducationalAndMethodicalWork.__name__.lower(): EducationalAndMethodicalWorkCalculation,
    ScientificAndInnovativeWork.__name__.lower(): ScientificAndInnovativeWorkCalculation,
    OrganizationalAndEducationalWork.__name__.lower(): OrganizationalAndEducationalWorkCalculation,
}


class Command(BaseCommand):
    help = "Calculate Teachers Places"

    def handle(self, *args, **options):
        report_period = ReportPeriod.objects.get(is_active=True)
        for report in REPORT_MODELS:
            for place, one in enumerate(
                report.objects.filter(generic_report_data__report_period=report_period).order_by("-result"), start=1
            ):
                report_place_name = report.__name__.lower() + "_place"
                if TeacherResults.objects.filter(generic_report_data=one.generic_report_data).exists():
                    total_result = TeacherResults.objects.filter(generic_report_data=one.generic_report_data).first()
                    setattr(total_result, report_place_name, place)
                    total_result.save()
                else:
                    TeacherResults.objects.create(
                        generic_report_data=one.generic_report_data,
                        **{report_place_name: place},
                    )

        for tr in TeacherResults.objects.filter(generic_report_data__report_period=report_period):
            tr.scores_sum = (
                1.5 * (tr.educationalandmethodicalwork_place or 0)
                + 1.5 * (tr.scientificandinnovativework_place or 0)
                + (tr.organizationalandeducationalwork_place or 0)
            )
            tr.save()

        for place, tr in enumerate(
            TeacherResults.objects.filter(generic_report_data__report_period=report_period).order_by("scores_sum"),
            start=1,
        ):
            tr.place = place
            tr.save()
