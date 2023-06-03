import csv

from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Imports tags from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', help='Path to CSV file')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        import_tags_from_csv(csv_path)
        self.stdout.write(
            self.style.SUCCESS('Successfully imported tags'))


def import_tags_from_csv(csv_path):
    print(f'Importing ingredients from {csv_path}')
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            name, color, slug = row
            tag = Tag.objects.create(name=name, color=color, slug=slug)
            tag.save()
