import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Imports ingredients from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', help='Path to CSV file')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        import_ingredients_from_csv(csv_path)
        self.stdout.write(
            self.style.SUCCESS('Successfully imported ingredients'))


def import_ingredients_from_csv(csv_path):
    print(f'Importing ingredients from {csv_path}')
    with open(csv_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            name, measurement_unit = row
            ingredient = Ingredient.objects.create(
                name=name, measurement_unit=measurement_unit)
            ingredient.save()
