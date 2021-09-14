import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from user_profile.models import Profile


class Command(BaseCommand):
    help = 'Export all users to csv file. Will be placed to /tmp/users_{timestamp}.csv'

    def handle(self, *args, **options):
        with open(f"/tmp/users_{datetime.now().strftime('%Y_%m_%d')}.csv", 'w', newline='') as csvfile:
            fieldnames = ["last_name", "first_name", "faculty", "department", "position", "date_joined"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for p in Profile.objects.all():
                writer.writerow(
                    {
                        "first_name": p.user.first_name,
                        "last_name": p.user.last_name,
                        "faculty": getattr(p.department, "faculty", None),
                        "department": p.department,
                        "position": p.position,
                        "date_joined": p.user.date_joined,
                    }
                )

        self.stdout.write("Success")
