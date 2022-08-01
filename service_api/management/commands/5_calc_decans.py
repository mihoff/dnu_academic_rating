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
    DecansResults,
)
from user_profile.models import Profile, Department, Position


class Command(BaseCommand):
    help = "Calculate Decans"

    def handle(self, *args, **options):
        report_period = ReportPeriod.objects.get(is_active=True)
        for own_place, t_result in enumerate(
            TeacherResults.objects.filter(
                generic_report_data__user__profile__position__cumulative_calculation=Position.BY_FACULTY
            ).order_by("-scores_sum"),
            start=1,
        ):
            faculty = FacultyResults.objects.get(
                report_period=report_period, faculty=t_result.generic_report_data.user.profile.department.faculty
            )

            sum_place = 2 * own_place + faculty.place

            if DecansResults.objects.filter(teacher_result=t_result).exists():
                decan = DecansResults.objects.get(teacher_result=t_result)
                decan.own_place = own_place
                decan.sum_place = sum_place
                decan.save()
            else:
                DecansResults.objects.create(
                    teacher_result=t_result,
                    own_place=own_place,
                    sum_place=sum_place,
                )

        for place, decan in enumerate(
            DecansResults.objects.filter(teacher_result__generic_report_data__report_period=report_period).order_by(
                "sum_place"
            ),
            start=1,
        ):
            decan.place = place
            decan.save()
