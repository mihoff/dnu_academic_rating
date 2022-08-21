from django.core.management.base import BaseCommand

from service_api.models import (
    ReportPeriod,
    TeacherResults,
    FacultyResults,
    DecansResults,
)
from user_profile.models import Position


class Command(BaseCommand):
    help = "Calculate Decans"

    def handle(self, *args, **options):
        report_period = ReportPeriod.objects.get(is_active=True)
        for t_result in TeacherResults.objects.filter(
            generic_report_data__user__profile__position__cumulative_calculation=Position.BY_FACULTY
        ):
            faculty = FacultyResults.objects.get(
                report_period=report_period, faculty=t_result.generic_report_data.user.profile.department.faculty
            )

            sum_place = 2 * t_result.scores_sum + faculty.places_sum_average

            if DecansResults.objects.filter(teacher_result=t_result).exists():
                decan = DecansResults.objects.get(teacher_result=t_result)
                decan.sum_place = sum_place
                decan.save()
            else:
                DecansResults.objects.create(
                    teacher_result=t_result,
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
