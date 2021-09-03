import logging

from django.db.models import Sum, Count

from service_api.calculations import BaseCalculation
from service_api.models import GenericReportData, REPORT_MODELS
from user_profile.models import Position, Profile

logger = logging.getLogger()


class GenericReportCalculation(BaseCalculation):

    def __init__(self, report: GenericReportData):
        self.report = report

    def get_result(self) -> float:
        result = 0
        for report in REPORT_MODELS:
            obj = report.objects.filter(generic_report_data=self.report).first()
            if not obj:
                continue

            obj.adjusted_result = obj.get_final_result()
            obj.save()

            result += obj.adjusted_result * obj.adjust_rate

        result = self.get_cumulative_result(result)

        return self.apply_rounding(result)

    def get_cumulative_result(self, result):
        try:
            cumulative_opt = self.report.user.profile.position.cumulative_calculation
        except Exception as e:
            logger.exception(e)
            return result

        if cumulative_opt is None:
            return result

        data = {"result__sum": 0, "pk__count": 1}
        if cumulative_opt == Position.BY_FACULTY:
            data = GenericReportData.objects.filter(
                user__profile__department__faculty=self.report.user.profile.department.faculty
            ).exclude(pk=self.report.pk).aggregate(Sum("result"), Count('pk'))
        elif cumulative_opt == Position.BY_DEPARTMENT:
            data = GenericReportData.objects.filter(
                user__profile__department=self.report.user.profile.department
            ).exclude(pk=self.report.pk).aggregate(Sum("result"), Count('pk'))

        return (result + data["result__sum"] / data["pk__count"]) / 2


class HeadsGetter:
    def __init__(self, department=None, faculty=None):
        self.department = department
        self.faculty = faculty

        self.head_of_faculty_profile = self.__get_head_of_faculty_profile()
        self.head_of_department_profile = self.__get_head_of_department_profile()

    def __get_head_of_faculty_profile(self):
        return Profile.objects.filter(
            department__faculty=self.faculty,
            position__cumulative_calculation=Position.BY_FACULTY
        ).first()

    def __get_head_of_department_profile(self):
        return Profile.objects.filter(
            department=self.department,
            position__cumulative_calculation=Position.BY_DEPARTMENT
        ).first()
