from typing import Optional, Union, Type

from django.contrib.auth.models import User
from django.db.models import Sum, Count

from service_api.calculations import BaseCalculation
from service_api.calculations.generic_report_calc import update_generic_report
from service_api.models import GenericReportData, ReportPeriod, BaseReportModel
from user_profile.models import Profile, Position


class HeadsGetter:
    def __init__(self, user: User):
        """
        user: User, by which heads are needed
        """
        self.department = user.profile.department
        self.faculty = user.profile.department.faculty

        self.head_of_faculty: User = self.__get_head_of_faculty()
        self.head_of_department: User = self.__get_head_of_department()

    def __get_head_of_faculty(self) -> Optional[User]:
        profile = Profile.objects.filter(
            department__faculty=self.faculty,
            position__cumulative_calculation=Position.BY_FACULTY
        ).first()
        if profile:
            return profile.user

    def __get_head_of_department(self) -> Optional[User]:
        profile = Profile.objects.filter(
            department=self.department,
            position__cumulative_calculation=Position.BY_DEPARTMENT
        ).first()
        if profile:
            return profile.user


class HeadCalculation:
    def __init__(self, head: User, report_period: ReportPeriod):
        self.head = head
        self.report_period = report_period

    def __get_cumulative_qs(
            self,
            report_cls: Type[BaseReportModel],
            opt: Union[Position.BY_FACULTY, Position.BY_DEPARTMENT]):

        if opt == Position.BY_DEPARTMENT:
            return report_cls.objects.filter(
                generic_report_data__report_period=self.report_period,
                generic_report_data__user__profile__department=self.head.profile.department)
        elif opt == Position.BY_FACULTY:
            return report_cls.objects.filter(
                generic_report_data__report_period=self.report_period,
                generic_report_data__user__profile__department__faculty=self.head.profile.department.faculty)

    def update(
            self,
            opt: Union[Position.BY_FACULTY, Position.BY_DEPARTMENT],
            report_models: tuple[Type[BaseReportModel]]):

        for report_model in report_models:
            report = report_model.objects.filter(
                generic_report_data__report_period=self.report_period,
                generic_report_data__user=self.head).first()
            if report is not None:
                data = self.__get_cumulative_qs(
                    report_model, opt
                ).exclude(pk=report.pk).aggregate(Sum("result"), Count('pk'))
                report.adjusted_result = BaseCalculation.apply_rounding(
                    (report.get_final_result() + ((data["result__sum"] or 0) / (data["pk__count"] or 1))) / 2)
                report.save()

        head_generic_report = GenericReportData.get_report(self.head, self.report_period)
        if head_generic_report:
            update_generic_report(head_generic_report, skip_adjustment=True)
