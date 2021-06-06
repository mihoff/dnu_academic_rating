import csv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

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
                user = User.objects.filter(email=row[self.email]).first()
                if user:
                    self.stdout.write(f"{user} already exists, make an update through the admin flow")
                    continue
                last_name, first_name = row[self.full_name].split(' ', maxsplit=1)
                user = User.objects.create_user(
                    username=row[self.email].strip(),
                    email=row[self.email].strip(),
                    first_name=first_name,
                    last_name=last_name,
                )

                faculty, _ = Faculty.objects.get_or_create(title=row[self.faculty].strip().lower())

                dep, _ = Department.objects.get_or_create(faculty=faculty, title=row[self.department].strip().lower())

                user.profile.department = dep
                user.profile.position = Position.objects.get(title=row[self.position].strip().lower())

                user.save()

        self.stdout.write("Success")
