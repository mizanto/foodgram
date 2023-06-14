import csv

from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Imports users from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', help='Path to CSV file')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        import_users_from_csv(csv_path)
        self.stdout.write(
            self.style.SUCCESS('Successfully imported users'))


def import_users_from_csv(csv_path):
    print(f'Importing users from {csv_path}')
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            email, username, first_name, last_name, password = row
            user = User.objects.create_user(
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            user.save()
