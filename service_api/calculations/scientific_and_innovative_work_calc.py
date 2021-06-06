from service_api.calculations import BaseCalculation
from service_api.models import ScientificAndInnovativeWork


class ScientificAndInnovativeWorkCalculation(BaseCalculation):

    def __init__(self, report: ScientificAndInnovativeWork):
        self.report = report

    def get_result(self) -> float:
        result = self.report.one_one
        return self.apply_rounding(result)
