from service_api.calculations import BaseCalculation
from service_api.models import OrganizationalAndEducationalWork


class OrganizationalAndEducationalWorkCalculation(BaseCalculation):
    def __init__(self, report: OrganizationalAndEducationalWork):
        self.report = report

    def get_result(self) -> float:
        result = (
            self.__calc_one()
            + self.__calc_two()
            + self.__calc_three()
            + self.__calc_four()
            + self.__calc_five()
            + self.__calc_six()
            + self.__calc_seven()
            + self.__calc_eight()
            + self.__calc_nine()
            + self.__calc_ten()
            + self.__calc_eleven()
            + self.__calc_twelve()
            + self.__calc_thirteen()
            + self.__calc_fourteen()
            + self.__calc_fifteen()
            + self.__calc_sixteen()
            + self.__calc_seventeen()
            + self.__calc_eighteen()
            + self.__calc_nineteen()
            + self.__calc_twenty()
            + self.__calc_twenty_one()
        )
        return self.apply_rounding(result)

    def __calc_one(self) -> float:
        r = {
            OrganizationalAndEducationalWork.NONE: 0,
            OrganizationalAndEducationalWork.HEAD: 100,
            OrganizationalAndEducationalWork.SECRETARY: 100,
            OrganizationalAndEducationalWork.MEMBER: 50,
        }.get(self.report.one_one) or 0
        return r

    def __calc_two(self) -> float:
        r = 100 if self.report.two_one else 0
        return r

    def __calc_three(self) -> float:
        r = 100 if self.report.three_one else 0
        return r

    def __calc_four(self) -> float:
        UNIVERSITY_POSITIONS = {
            OrganizationalAndEducationalWork.NONE: 0,
            OrganizationalAndEducationalWork.HEAD: 50,
            OrganizationalAndEducationalWork.SECRETARY: 50,
            OrganizationalAndEducationalWork.MEMBER: 25,
        }
        FACULTY_POSITIONS = {
            OrganizationalAndEducationalWork.NONE: 0,
            OrganizationalAndEducationalWork.HEAD: 30,
            OrganizationalAndEducationalWork.SECRETARY: 30,
            OrganizationalAndEducationalWork.MEMBER: 15,
        }

        r = (
            UNIVERSITY_POSITIONS.get(self.report.four_one)
            + UNIVERSITY_POSITIONS.get(self.report.four_two)
            + FACULTY_POSITIONS.get(self.report.four_three)
            + UNIVERSITY_POSITIONS.get(self.report.four_four)
            + FACULTY_POSITIONS.get(self.report.four_five)
            + FACULTY_POSITIONS.get(self.report.four_six)
        )
        return r

    def __calc_five(self) -> float:
        r = (250 if self.report.five_one else 0) + (150 if self.report.five_two else 0)
        return r

    def __calc_six(self) -> float:
        r = 10 * self.report.six_one
        return r

    def __calc_seven(self) -> float:
        r = 10 * self.report.seven_one
        return r

    def __calc_eight(self) -> float:
        r = 50 * self.report.eight_one / 12
        return r

    def __calc_nine(self) -> float:
        LEVELS_RATE = {
            OrganizationalAndEducationalWork.NONE: 0,
            OrganizationalAndEducationalWork.HEAD: 80,
            OrganizationalAndEducationalWork.SECRETARY: 60,
            OrganizationalAndEducationalWork.MEMBER: 40,
        }
        r = LEVELS_RATE.get(self.report.nine_one) or 0
        return r

    def __calc_ten(self) -> float:
        LEVELS_RATE = {
            OrganizationalAndEducationalWork.NONE: 0,
            OrganizationalAndEducationalWork.HEAD: 50,
            OrganizationalAndEducationalWork.SECRETARY: 35,
            OrganizationalAndEducationalWork.MEMBER: 25,
        }
        r = LEVELS_RATE.get(self.report.ten_one) or 0
        return r

    def __calc_eleven(self) -> float:
        r = 250 if self.report.eleven_one else 0 + 100 if self.report.eleven_two else 0
        return r

    def __calc_twelve(self) -> float:
        r = self.report.twelve_one
        return r

    def __calc_thirteen(self) -> float:
        r = (
            (300 if self.report.thirteen_one else 0)
            + (250 if self.report.thirteen_two else 0)
            + (30 if self.report.thirteen_three else 0)
            + (10 * self.report.thirteen_four)
            if (10 * self.report.thirteen_four < 150)
            else 150
            + 20 * self.report.thirteen_five
            + 15 * self.report.thirteen_six
            + 5 * self.report.thirteen_seven
            + 15 * self.report.thirteen_eight
        )
        return r

    def __calc_fourteen(self) -> float:
        r = 50 * self.report.fourteen_one
        return r

    def __calc_fifteen(self) -> float:
        r = 30 * self.report.fifteen_one
        return r

    def __calc_sixteen(self) -> float:
        r = 50 if self.report.sixteen_one else 0
        return r

    def __calc_seventeen(self) -> float:
        r = 50 if self.report.seventeen_one else 0
        return r

    def __calc_eighteen(self) -> float:
        r = self._divide(50, self.report.eighteen_one)
        return r

    def __calc_nineteen(self) -> float:
        r = 100 * self.report.nineteen_one
        return r

    def __calc_twenty(self) -> float:
        r = (
            200
            if self.report.twenty_zero_one
            else 0 + 100
            if self.report.twenty_zero_two
            else 0 + 75
            if self.report.twenty_zero_three
            else 0
        )
        return r

    def __calc_twenty_one(self) -> float:
        r = (
            150
            if self.report.twenty_one_one
            else 0 + 100
            if self.report.twenty_one_two
            else 0 + 30
            if self.report.twenty_one_three
            else 0
        )
        return r
