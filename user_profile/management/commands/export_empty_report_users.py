import csv
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q

from user_profile.models import Profile


class Command(BaseCommand):
    help = 'Export all users to csv file. Will be placed to /tmp/export_empty_report_users_{timestamp}.csv'

    def handle(self, *args, **options):
        f_name = f"/tmp/export_empty_report_users_{datetime.now().strftime('%Y_%m_%d')}.csv"
        with open(f_name, 'w', newline='', encoding='utf8') as f:
            fieldnames = ["Прізвище", "Ім'я По батькові", "Факультет", "Кафедра", "Посада", "Був в системі"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()

            for p in Profile.objects.filter(
                    Q(user__genericreportdata__isnull=True) |
                    Q(user__microsoft_account__isnull=True) |
                    Q(user__genericreportdata__educationalandmethodicalwork__isnull=True) |
                    Q(user__genericreportdata__scientificandinnovativework__isnull=True) |
                    Q(user__genericreportdata__organizationalandeducationalwork__isnull=True)
            ):
                writer.writerow(
                    {
                        "Прізвище": p.user.last_name,
                        "Ім'я По батькові": p.user.first_name,
                        "Факультет": getattr(p.department, "faculty", None),
                        "Кафедра": p.department,
                        "Посада": p.position,
                        "Був в системі": getattr(p.user, "microsoft_account", False) and "Так" or "Ні"
                    }
                )

        self.stdout.write("Success")
