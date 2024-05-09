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
        print(self.report.two_one, self.report.two_two, self.report.two_three, self.report.two_four)
        r = 50 * self.report.two_one + 30 * self.report.two_two + 25 * self.report.two_three + 10 * self.report.two_four
        return r

    def _calc_three(self) -> float:
        r = 50 * self.report.three_one + int(50 * 0.2) * self.report.three_two
        return r

    def _calc_four(self) -> float:
        r = self.LEVELS_RATE.get(self.report.eight_one) or 0
        return r

    def _calc_five(self) -> float:
        r = 100 * self.report.five_one + 30 * self.report.five_two + 150 * self.report.five_three + 50 * self.report.five_four
        return r

    def _calc_six(self) -> float:
        r = (
            self._multiply_complex(25 / 100, self.report.six_one)
            + self._multiply_complex(25 * 0.3 / 100, self.report.six_two)
            + self._multiply_complex(20 / 100, self.report.six_three)
            + self._multiply_complex(20 * 0.3 / 100, self.report.six_four)
        )
        return r
    
    def _calc_seven(self) -> float:
        r = (
            self._multiply_complex(50 / 100, self.report.seven_one)
            + self._multiply_complex(50 * 0.3 / 100, self.report.seven_two)
            + self._multiply_complex(100 / 100, self.report.seven_three)
            + self._multiply_complex(100 * 0.3 / 100, self.report.seven_four)
            + self._multiply_complex(40 / 100, self.report.seven_five)
            + self._multiply_complex(40 * 0.3 / 100, self.report.seven_six)
            + self._multiply_complex(80 / 100, self.report.seven_seven)
            + self._multiply_complex(80 * 0.3 / 100, self.report.seven_eight)
        )
        return r

    def _calc_eight(self) -> float:
        r = 1 * self.report.eight_one + 0.5 * self.report.eight_two
        return r

    def _calc_nine(self) -> float:
        r = 15 * self.report.nine_one
        return r

    def _calc_ten(self) -> float:
        r = 30 * self.report.ten_one + 20 * self.report.ten_two + 40 * self.report.ten_three
        return r

    def _calc_eleven(self) -> float:
        r = 4 * self.report.eleven_one
        return r

    def _calc_twelve(self) -> float:
        r = 15 * self.report.twelve_one
        return r

    def _calc_thirteen(self) -> float:
        r = 100 * self.report.thirteen_one + 50 * self.report.thirteen_two
        return r

    def _calc_fourteen(self) -> float:
        r = (
            100 * self.report.fourteen_one + 50 * self.report.fourteen_two + 60 * self.report.fourteen_three 
            + 30 * self.report.fourteen_four + 30 * self.report.fourteen_five + 15 * self.report.fourteen_six
        )
        return r

    def _calc_fifteen(self) -> float:
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
            ).get(self.report.fifteen_one)
            or 0
        )
        return r

    def _students_result(self) -> float:
        r = (self.report.generic_report_data.students_rating or 0) * 2
        return r
