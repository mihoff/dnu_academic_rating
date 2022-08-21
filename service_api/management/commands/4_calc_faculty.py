from django.core.management.base import BaseCommand
from django.db.models import Sum, Count

from service_api.models import (
    ReportPeriod,
    TeacherResults,
    FacultyResults,
)
from user_profile.models import Position


class Command(BaseCommand):
    help = "Calculate Faculty Places"

    def handle(self, *args, **options):
        report_period = ReportPeriod.objects.get(is_active=True)
        for t_result in (
            TeacherResults.objects.filter(generic_report_data__report_period=report_period)
            .exclude(generic_report_data__user__profile__position__cumulative_calculation=Position.BY_FACULTY)
            .values("generic_report_data__user__profile__department__faculty")
            .annotate(Sum("scores_sum"), Count("scores_sum"))
        ):
            if FacultyResults.objects.filter(
                report_period=report_period,
                faculty_id=t_result["generic_report_data__user__profile__department__faculty"],
            ).exists():
                faculty = FacultyResults.objects.filter(
                    report_period=report_period,
                    faculty_id=t_result["generic_report_data__user__profile__department__faculty"],
                ).first()
                faculty.places_sum = t_result["scores_sum__sum"]
                faculty.places_sum_count = t_result["scores_sum__count"]
                faculty.places_sum_average = t_result["scores_sum__sum"] / t_result["scores_sum__count"]
                faculty.save()
            else:
                FacultyResults.objects.create(
                    report_period=report_period,
                    faculty_id=t_result["generic_report_data__user__profile__department__faculty"],
                    places_sum=t_result["scores_sum__sum"],
                    places_sum_count=t_result["scores_sum__count"],
                    places_sum_average=t_result["scores_sum__sum"] / t_result["scores_sum__count"],
                )

        for place, faculty_result in enumerate(
            FacultyResults.objects.filter(report_period=report_period).order_by("places_sum_average"), start=1
        ):
            faculty_result.place = place
            faculty_result.save()
