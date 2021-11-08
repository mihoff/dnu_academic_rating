from datetime import datetime

from django.core.management.base import BaseCommand
from service_api.models import GenericReportData, REPORT_MODELS, ReportPeriod


class Command(BaseCommand):
    help = "Calculate places for the University"

    def add_arguments(self, parser):
        parser.add_argument('--report-period', type=str)

    def handle(self, *args, **options):
        start_ts = datetime.now()
        report_period = ReportPeriod.objects.get(report_period=options["report_period"])
        total_count = GenericReportData.objects.filter(report_period=report_period).count()
        self.stdout.write(f"Total count {total_count}")

        for report_cls in REPORT_MODELS:
            self.stdout.write(f"Start calculating report {report_cls.__name__} '{report_cls.NAME}'...", ending=" ")
            for idx, report in enumerate(report_cls.objects.order_by("-adjusted_result"), start=1):
                report.place = idx
                report.save()
            self.stdout.write("done")

        dummy_report = type("dummy_report", (), {"place": total_count})
        for g_report in GenericReportData.objects.filter(report_period=report_period):
            g_report.place = sum(getattr(g_report, r.__name__.lower(), dummy_report).place for r in REPORT_MODELS)
            g_report.save()

        self.stdout.write(f"Done. Time spent {(datetime.now() - start_ts).seconds} seconds")
