from service_api.calculations import BaseCalculation
from service_api.models import EducationalAndMethodicalWork


class EducationalAndMethodicalWorkCalculation(BaseCalculation):
    LEVELS_RATE = {
        EducationalAndMethodicalWork.LEVEL_ONE: 60,
        EducationalAndMethodicalWork.LEVEL_TWO: 40,
        EducationalAndMethodicalWork.LEVEL_THREE: 20,
    }

    def __init__(self, report: EducationalAndMethodicalWork):
        self.report = report

    def get_result(self):
        result: float = \
            self.__calc_one() + self.__calc_two() + self.__calc_three() + self.__calc_four() + self.__calc_five() + \
            self.__calc_six() + self.__calc_seven() + self.__calc_eight() + self.__calc_nine() + self.__calc_ten() + \
            self.__calc_eleven() + self.__calc_twelve() + self.__calc_thirteen() + self.__calc_fourteen() + \
            self.__calc_fifteen() + self.__calc_sixteen() + self.__calc_seventeen() + self.__calc_eighteen() + \
            self.__calc_nineteen()

        return self.apply_rounding(result)

    def __calc_one(self) -> float:
        r = 0
        annual_workload = self.report.generic_report_data.report_period.annual_workload
        if annual_workload:
            r = 600 * (self.report.one_one / annual_workload) + \
                250 * ((self.report.one_three - self.report.one_one) / annual_workload) + \
                600 * (self.report.one_two / annual_workload)
        return r

    def __calc_two(self) -> float:
        r = self._multiply(4, self.report.two_two)
        return r

    def __calc_three(self) -> float:
        r = 50 * self.report.three_one + \
            15 * self.report.three_two + \
            10 * self.report.three_three
        return r

    def __calc_four(self) -> float:
        r = self._divide(50, self.report.four_one)
        return r

    def __calc_five(self) -> float:
        r = self._multiply(5, self.report.five_one) + \
            self._multiply(5, self.report.five_two)
        return r

    def __calc_six(self) -> float:
        r = 80 if self.report.six_one else 0
        return r

    def __calc_seven(self) -> float:
        """N * V * K"""
        r = self._multiply_complex(14 / 100, self.report.seven_one) + \
            self._multiply_complex(12 / 100, self.report.seven_two)
        return r

    def __calc_eight(self) -> float:
        r = self.LEVELS_RATE.get(self.report.eight_one) or 0
        return r

    def __calc_nine(self) -> float:
        return 0

    def __calc_ten(self) -> float:
        r = self._divide(50, self.report.ten_one) + \
            self._divide(10, self.report.ten_two)
        return r

    def __calc_eleven(self) -> float:
        return 0

    def __calc_twelve(self) -> float:
        r = self._multiply(150 / 100, self.report.twelve_one)
        return r

    def __calc_thirteen(self) -> float:
        r = self._multiply(200 / 100, self.report.thirteen_one)
        return r

    def __calc_fourteen(self) -> float:
        r = self._multiply(50 / 100, self.report.fourteen_one) + \
            self._multiply(10 / 100, self.report.fourteen_two)
        return r

    def __calc_fifteen(self) -> float:
        r = self._multiply(50 / 100, self.report.fifteen_one) + \
            self._multiply(10 / 100, self.report.fifteen_two)
        return r

    def __calc_sixteen(self) -> float:
        r = self._multiply(50 / 100, self.report.sixteen_one) + \
            self._multiply(50 * .2 / 100, self.report.sixteen_two)
        return r

    def __calc_seventeen(self) -> float:
        return 0

    def __calc_eighteen(self) -> float:
        r = 30 * self.report.eighteen_one
        return r

    def __calc_nineteen(self) -> float:
        return 0
