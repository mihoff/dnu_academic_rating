from service_api.calculations import BaseCalculation
from service_api.models import EducationalAndMethodicalWork


class EducationalAndMethodicalWorkCalculation(BaseCalculation):
    POSITION_RATES = {
        EducationalAndMethodicalWork.PROFESSOR: 120,
        EducationalAndMethodicalWork.DOCENT: 60
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
        if self.report.one_four:
            r = 600 * (self.report.one_one / self.report.one_four) + \
                250 * ((self.report.one_three - self.report.one_one) / self.report.one_four) + \
                600 * (self.report.one_two / self.report.one_four)
        return r

    def __calc_two(self) -> float:
        r = self._multiply(2, self.report.two_one) + \
            self._multiply(4, self.report.two_two) + \
            self._multiply(10, self.report.two_three)
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
        r = self.report.six_one
        return r

    def __calc_seven(self) -> float:
        """N * V * K"""
        r = self._multiply_complex(14, self.report.seven_one) + \
            self._multiply_complex(12, self.report.seven_two) + \
            self._multiply_complex(20, self.report.seven_three) + \
            self._multiply_complex(16, self.report.seven_four) + \
            self._multiply_complex(24, self.report.seven_five) + \
            self._multiply_complex(18, self.report.seven_six)
        return r

    def __calc_eight(self) -> float:
        r = 60 + self.report.eight_one + \
            40 + self.report.eight_two + \
            20 * self.report.eight_three
        return r

    def __calc_nine(self) -> float:
        r = self._multiply(150, self.report.nine_one) + \
            self._multiply(30, self.report.nine_two)
        return r

    def __calc_ten(self) -> float:
        r = self._divide(50, self.report.ten_one) + \
            self._divide(10, self.report.ten_two) + \
            self._divide(50, self.report.ten_three) * .8 + \
            self._divide(10, self.report.ten_four) * .8
        return r

    def __calc_eleven(self) -> float:
        r = self._multiply(50, self.report.eleven_one) + \
            self._multiply(50, self.report.eleven_two) * .8
        return r

    def __calc_twelve(self) -> float:
        r = self._multiply(150, self.report.twelve_one)
        return r

    def __calc_thirteen(self) -> float:
        r = self._multiply(200, self.report.thirteen_one) + \
            self._multiply(300, self.report.thirteen_two)
        return r

    def __calc_fourteen(self) -> float:
        r = self._multiply(50, self.report.fourteen_one) + \
            self._multiply(50, self.report.fourteen_two) * .8
        return r

    def __calc_fifteen(self) -> float:
        r = self._multiply(50, self.report.fifteen_one) + \
            self._multiply(50, self.report.fifteen_two) * .8
        return r

    def __calc_sixteen(self) -> float:
        r = self._multiply(50, self.report.sixteen_one) + \
            self._multiply(50, self.report.sixteen_two) * .8 + \
            self._multiply(30, self.report.sixteen_one) + \
            self._multiply(30, self.report.sixteen_two) * .8 + \
            self._multiply(60, self.report.sixteen_one) + \
            self._multiply(60, self.report.sixteen_two) * .8
        return r

    def __calc_seventeen(self) -> float:
        r = self._multiply(50, self.report.seventeen_one)
        return r

    def __calc_eighteen(self) -> float:
        r = 30 * self.report.eighteen_one
        return r

    def __calc_nineteen(self) -> float:
        r = self.POSITION_RATES.get(self.report.nineteen_one) or .0
        return r
