from django.core.management.base import BaseCommand
from django.db.models import Sum, Count

from service_api.models import (
    ReportPeriod,
    TeacherResults,
    HeadsOfDepartmentsResults,
)
from user_profile.models import Department, Position


class Command(BaseCommand):
    help = "Calculate Heads of Departments"

    def handle(self, *args, **options):
        report_period = ReportPeriod.objects.get(is_active=True)
        for department in Department.objects.all():
            self.stdout.write(f"Calculating for {department.title}...", ending=" ")
            teacher_result = TeacherResults.objects.filter(
                generic_report_data__user__profile__department=department,
                generic_report_data__user__profile__position__cumulative_calculation=Position.BY_DEPARTMENT,
                generic_report_data__report_period=report_period,
            ).first()
            if not teacher_result:
                self.stdout.write("ERROR")
                continue

            related_teachers_sum = (
                TeacherResults.objects.filter(
                    generic_report_data__user__profile__department=department,
                    generic_report_data__report_period=report_period,
                )
                .exclude(pk=teacher_result.pk)
                .aggregate(Sum("scores_sum"), Count("pk"))
            )

            if HeadsOfDepartmentsResults.objects.filter(teacher_result=teacher_result).exists():
                head = HeadsOfDepartmentsResults.objects.filter(teacher_result=teacher_result).first()
                head.related_to_department_sum = related_teachers_sum["scores_sum__sum"]
                head.related_to_department_count = related_teachers_sum["pk__count"]
                head.scores_sum = related_teachers_sum["scores_sum__sum"] / related_teachers_sum["pk__count"] + 2 * (
                    teacher_result.scores_sum or 0
                )
                head.save()
            else:
                HeadsOfDepartmentsResults.objects.create(
                    teacher_result=teacher_result,
                    related_to_department_sum=related_teachers_sum["scores_sum__sum"],
                    related_to_department_count=related_teachers_sum["pk__count"],
                    scores_sum=related_teachers_sum["scores_sum__sum"] / related_teachers_sum["pk__count"]
                    + 2 * (teacher_result.scores_sum or 0),
                )
            self.stdout.write(f"calculated", style_func=self.style.SUCCESS)

        for place, head in enumerate(
            HeadsOfDepartmentsResults.objects.filter(
                teacher_result__generic_report_data__report_period=report_period
            ).order_by("-scores_sum"),
            start=1,
        ):
            head.place = place
            head.save()
