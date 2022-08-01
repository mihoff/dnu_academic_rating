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
        result: float = (
            self._calc_one()
            + self._calc_two()
            + self._calc_three()
            + self._calc_four()
            + self._calc_five()
            + self._calc_six()
            + self._calc_seven()
            + self._calc_eight()
            + self._calc_nine()
            + self._calc_ten()
            + self._calc_eleven()
            + self._calc_twelve()
            + self._calc_thirteen()
            + self._calc_fourteen()
            + self._calc_fifteen()
            + self._calc_sixteen()
            + self._calc_seventeen()
            + self._calc_eighteen()
            + self._calc_nineteen()
            + self._calc_twenty_one()
            + self._calc_twenty_two()
            + self._calc_twenty_three()
            + self._students_result()
        )

        return self.apply_rounding(result)

    def _calc_one(self) -> float:
        r = 0
        annual_workload = self.report.generic_report_data.report_period.annual_workload
        if annual_workload:
            r = (
                600 * (self.report.one_one / annual_workload)
                + 250 * ((self.report.one_three - self.report.one_one) / annual_workload)
                + 600 * (self.report.one_two / annual_workload)
            )
        return r

    def _calc_two(self) -> float:
        r = self._multiply(150 / 100, self.report.two_one) + self._multiply(150 * 0.3 / 100, self.report.two_two)
        return r

    def _calc_three(self) -> float:
        r = (
            self._divide(50, self.report.three_one)
            + self._divide(10, self.report.three_two)
            + self._divide(int(50 * 0.2), self.report.three_three)
            + self._divide(int(10 * 0.2), self.report.three_four)
        )
        return r

    def _calc_four(self) -> float:
        r = self.LEVELS_RATE.get(self.report.eight_one) or 0
        return r

    def _calc_five(self) -> float:
        r = self._multiply(200 / 100, self.report.five_one) + self._multiply(300 / 100, self.report.five_two)
        return r

    def _calc_six(self) -> float:
        r = (
            self._multiply_complex(14 / 100, self.report.six_one)
            + self._multiply_complex(12 / 100, self.report.six_two)
            + self._multiply_complex(20 / 100, self.report.six_three)
            + self._multiply_complex(16 / 100, self.report.six_four)
            + self._multiply_complex(24 / 100, self.report.six_five)
            + self._multiply_complex(18 / 100, self.report.six_six)
        )
        return r

    def _calc_seven(self) -> float:
        """N * V * K"""
        r = self._multiply(5, self.report.seven_one) + self._multiply(10, self.report.seven_two)
        return r

    def _calc_eight(self) -> float:
        r = self._multiply(20 / 100, self.report.eight_one) + self._multiply(5 / 100, self.report.eight_two)
        return r

    def _calc_nine(self) -> float:
        r = (
            5 * self.report.nine_one / self.report.generic_report_data.assignment
            + 1 * self.report.nine_two / self.report.generic_report_data.assignment
        )
        return r

    def _calc_ten(self) -> float:
        r = (
            self._multiply(50 / 100, self.report.ten_one) / self.report.generic_report_data.assignment
            + self._multiply(10 / 100, self.report.ten_two) / self.report.generic_report_data.assignment
        )
        return r

    def _calc_eleven(self) -> float:
        r = (
            10 * self.report.eleven_one / self.report.generic_report_data.assignment
            + 2 * self.report.eleven_two / self.report.generic_report_data.assignment
        )
        return r

    def _calc_twelve(self) -> float:
        r = (
            self._multiply(50 / 100, self.report.twelve_one) / self.report.generic_report_data.assignment
            + self._multiply(10 / 100, self.report.twelve_two) / self.report.generic_report_data.assignment
        )
        return r

    def _calc_thirteen(self) -> float:
        r = self._multiply(50 / 100, self.report.thirteen_one) / self.report.generic_report_data.assignment
        return r

    def _calc_fourteen(self) -> float:
        r = (
            self._multiply(50 / 100, self.report.fourteen_one) / self.report.generic_report_data.assignment
            + self._multiply(10 / 100, self.report.fourteen_two) / self.report.generic_report_data.assignment
        )
        return r

    def _calc_fifteen(self) -> float:
        r = (
            self._multiply(50 / 100, self.report.fifteen_one)
            + self._multiply(10 / 100, self.report.fifteen_two)
            + self._multiply(30 / 100, self.report.fifteen_three)
            + self._multiply(6 / 100, self.report.fifteen_four)
            + self._multiply(60 / 100, self.report.fifteen_five)
            + self._multiply(12 / 100, self.report.fifteen_six)
        )
        return r

    def _calc_sixteen(self) -> float:
        r = self._multiply(4, self.report.sixteen_one) + self._multiply(10, self.report.sixteen_two)
        return r

    def _calc_seventeen(self) -> float:
        r = 50 * self.report.seventeen_one + 15 * self.report.seventeen_two + 10 * self.report.seventeen_three
        return r

    def _calc_eighteen(self) -> float:
        r = 60 if self.report.eighteen_one else 0 + (200 / self.report.eighteen_two) if self.report.eighteen_two else 0
        return r

    def _calc_nineteen(self) -> float:
        r = 100 * self.report.nineteen_one + 60 * self.report.nineteen_two + 30 * self.report.nineteen_three
        return r

    def _calc_twenty(self) -> float:
        r = 250 * self.report.twenty_one + 150 * self.report.twenty_two + 75 * self.report.twenty_three
        return r

    def _calc_twenty_one(self) -> float:
        r = 500 * self.report.twenty_one_one + 300 * self.report.twenty_one_two + 150 * self.report.twenty_one_three
        return r

    def _calc_twenty_two(self) -> float:
        r = 200 * self.report.twenty_two_one + 100 * self.report.twenty_two_two
        return r

    def _calc_twenty_three(self) -> float:
        r = (
            dict(
                (
                    (EducationalAndMethodicalWork.NONE, 0),
                    (EducationalAndMethodicalWork.HONORED_WORKER_OF_EDUCATION_OF_UKRAINE, 300),
                    (EducationalAndMethodicalWork.EXCELLENT_EDUCATION, 150),
                    (EducationalAndMethodicalWork.HONORED_PROFESSOR_LECTURER_OF_DNU, 100),
                    (EducationalAndMethodicalWork.HONORED_LECTURER_OF_DNU, 70),
                    (EducationalAndMethodicalWork.PROFESSOR, 120),
                    (EducationalAndMethodicalWork.DOCENT, 60),
                )
            ).get(self.report.twenty_three_one)
            or 0
        )
        return r

    def _students_result(self) -> float:
        r = (self.report.generic_report_data.students_rating or 0) * 2
        return r
