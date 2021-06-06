from service_api.calculations import BaseCalculation
from service_api.models import GenericReportData, EducationalAndMethodicalWork, ScientificAndInnovativeWork, \
    OrganizationalAndEducationalWork


class GenericReportCalculation(BaseCalculation):

    def __init__(self, report: GenericReportData):
        self.report = report

    def get_result(self) -> float:
        result = 0
        for report in (EducationalAndMethodicalWork, ScientificAndInnovativeWork, OrganizationalAndEducationalWork):
            obj = report.objects.filter(generic_report_data=self.report).first()
            if obj:
                result += obj.get_final_result()

        return self.apply_rounding(result)
