import logging

from service_api.calculations import BaseCalculation
from service_api.models import GenericReportData, REPORT_MODELS

logger = logging.getLogger()


class GenericReportCalculation(BaseCalculation):

    def __init__(self, report: GenericReportData, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report = report

    def get_result(self) -> float:
        result = 0
        for report in REPORT_MODELS:
            obj = report.objects.filter(generic_report_data=self.report).first()
            if not obj:
                continue

            if not self.skip_adjustment:
                obj.adjusted_result = obj.get_final_result()
                obj.save()

            result += obj.adjusted_result * obj.adjust_rate

        return self.apply_rounding(result)


def update_generic_report(generic_report: GenericReportData, skip_adjustment: bool = False):
    calc_obj = GenericReportCalculation(generic_report, skip_adjustment)
    generic_report.result = calc_obj.get_result()
    generic_report.save()
