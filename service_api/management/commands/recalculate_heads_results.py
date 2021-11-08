from datetime import datetime

from django.core.management.base import BaseCommand

from service_api.calculations.heads_calc import HeadsGetter, HeadCalculation
from service_api.models import ReportPeriod, REPORT_MODELS
from user_profile.models import Profile, Position


class Command(BaseCommand):
    help = "Recalculate results of Heads"

    def add_arguments(self, parser):
        parser.add_argument('--report-period', type=str)

    def handle(self, *args, **options):
        start_ts = datetime.now()
        report_period = ReportPeriod.objects.get(report_period=options["report_period"])
        total_count = Profile.objects.filter(position__cumulative_calculation=Position.BY_DEPARTMENT).count()
        self.stdout.write(f"Total count {total_count}")

        for profile in Profile.objects.filter(position__cumulative_calculation=Position.BY_DEPARTMENT):
            heads = HeadsGetter(profile.user)

            heads_calc = HeadCalculation(heads.head_of_department, report_period)
            heads_calc.update(opt=Position.BY_DEPARTMENT, report_models=REPORT_MODELS)

            heads_calc = HeadCalculation(heads.head_of_faculty, report_period)
            heads_calc.update(opt=Position.BY_FACULTY, report_models=REPORT_MODELS)

        self.stdout.write(f"Done. Time spent {(datetime.now() - start_ts).seconds} seconds")
