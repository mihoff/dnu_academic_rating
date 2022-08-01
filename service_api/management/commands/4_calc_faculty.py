import csv
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q, Sum, Count

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
    HeadsOfDepartmentsResults,
    FacultyResults,
)
from user_profile.models import Profile, Department, Position


class Command(BaseCommand):
    help = "Calculate Faculty Places"

    def handle(self, *args, **options):
        report_period = ReportPeriod.objects.get(is_active=True)
        for t_result in (
            TeacherResults.objects.filter(generic_report_data__report_period=report_period)
            .exclude(generic_report_data__user__profile__position__cumulative_calculation=Position.BY_FACULTY)
            .values("generic_report_data__user__profile__department__faculty")
            .annotate(Sum("scores_sum"))
        ):
            if FacultyResults.objects.filter(
                report_period=report_period,
                faculty_id=t_result["generic_report_data__user__profile__department__faculty"],
            ).exists():
                faculty = FacultyResults.objects.filter(
                    report_period=report_period,
                    faculty_id=t_result["generic_report_data__user__profile__department__faculty"],
                ).first()
                faculty.scores_sum = t_result["scores_sum__sum"]
                faculty.save()
            else:
                FacultyResults.objects.create(
                    report_period=report_period,
                    faculty_id=t_result["generic_report_data__user__profile__department__faculty"],
                    scores_sum=t_result["scores_sum__sum"],
                )

        for place, faculty_result in enumerate(
            FacultyResults.objects.filter(report_period=report_period).order_by("-scores_sum"), start=1
        ):
            faculty_result.place = place
            faculty_result.save()
