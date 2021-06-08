import csv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from user_profile.models import Position, Department, Faculty


class Command(BaseCommand):
    help = 'Uploading users in the system'

    full_name = "ПІБ"
    email = "Логін"
    position = "посада"
    department = "кафедра"
    faculty = "факультет"

    def add_arguments(self, parser):
        parser.add_argument('--file-path', type=str)

    def handle(self, *args, **options):
        with open(options['file_path']) as f:
            file_reader = csv.DictReader(f, delimiter=';')
            for row in file_reader:
                email = row[self.email].lower().strip()
                user = User.objects.filter(email=email).first()
                if user:
                    self.stdout.write(f"{user} already exists, make an update through the admin flow")
                last_name, first_name = row[self.full_name].split(' ', maxsplit=1)
                if user:
                    user.first_name = first_name
                    user.last_name = last_name
                else:
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                    )

                faculty, _ = Faculty.objects.get_or_create(title=row[self.faculty].strip().lower())

                dep, _ = Department.objects.get_or_create(faculty=faculty, title=row[self.department].strip().lower())

                user.profile.department = dep
                user.profile.position = Position.objects.get(title=row[self.position].strip().lower())

                user.save()

        self.stdout.write("Success")
