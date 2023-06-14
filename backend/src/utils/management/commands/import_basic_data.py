from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.models import User
import csv
import json


class Command(BaseCommand):
    help = 'Imports data from CSV files and generates recipes'

    def add_arguments(self, parser):
        parser.add_argument(
            'data_path',
            nargs='?',
            default='../../data/',
            help='Path to data directory'
        )

    def handle(self, *args, **options):
        data_path = options['data_path']
        self.import_users_from_csv(data_path + 'users.csv')
        self.stdout.write(self.style.SUCCESS('Imported users'))
        self.import_tags_from_csv(data_path + 'tags.csv')
        self.stdout.write(self.style.SUCCESS('Imported tags'))
        self.import_ingredients_from_csv(data_path + 'ingredients.csv')
        self.stdout.write(self.style.SUCCESS('Imported ingredients'))
        recipes_data = self.load_recipes_from_json(data_path + 'recipes.json')
        self.generate_recipes_for_all_users(recipes_data, data_path)
        self.stdout.write(self.style.SUCCESS('Generated recipes'))

    def import_users_from_csv(self, csv_path):
        self.stdout.write(self.style.NOTICE(
            f'Importing users from {csv_path}...'))
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                email, username, first_name, last_name, password = row
                try:
                    User.objects.get(username=username)
                except ObjectDoesNotExist:
                    user = User.objects.create_user(
                        email=email,
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        password=password
                    )
                    user.save()

    def import_tags_from_csv(self, csv_path):
        self.stdout.write(self.style.NOTICE(
            f'Importing tags from {csv_path}...'))
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name, color, slug = row
                try:
                    Tag.objects.get(name=name)
                except ObjectDoesNotExist:
                    tag = Tag.objects.create(name=name, color=color, slug=slug)
                    tag.save()

    def import_ingredients_from_csv(self, csv_path):
        self.stdout.write(self.style.NOTICE(
            f'Importing ingredients from {csv_path}...'))
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name, measurement_unit = row
                ingredient = Ingredient.objects.filter(name=name).first()
                if ingredient is None:
                    ingredient = Ingredient.objects.create(
                        name=name, measurement_unit=measurement_unit)
                    ingredient.save()

    def load_recipes_from_json(self, json_path):
        self.stdout.write(self.style.NOTICE(
            f'Loading recipes from {json_path}...'))
        with open(json_path, 'r') as jsonfile:
            return json.load(jsonfile)

    def generate_recipes_for_all_users(self, recipes_data, data_path):
        users = User.objects.all()
        user_count = users.count()
        for i, recipe_data in enumerate(recipes_data['recipes']):
            user = users[i % user_count]
            self.generate_recipe_for_user(user, recipe_data, data_path)

    def generate_recipe_for_user(self, user, recipe_data, data_path):
        recipe_name = recipe_data['name']
        if Recipe.objects.filter(name=recipe_name).exists():
            return

        for ingredient_data in recipe_data['ingredients']:
            ingredient, created = Ingredient.objects.get_or_create(
                name=ingredient_data['name'],
                defaults={'measurement_unit': ingredient_data['unit']}
            )

        tags = [Tag.objects.get(name=tag_name) for tag_name in recipe_data['tags']]

        recipe = Recipe.objects.create(
            author=user,
            name=recipe_name,
            text=recipe_data['text'],
            cooking_time=recipe_data['cooking_time'],
        )

        image_name = recipe_data['slug'] + '.png'
        image_path = f"{data_path}img/{image_name}"
        self.stdout.write(self.style.NOTICE(
            f'Importing image for {recipe.name} from {image_path}...'))
        with open(image_path, 'rb') as f:
            recipe.image.save(image_name, f)
            recipe.save()

        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

        for ingredient_data in recipe_data['ingredients']:
            ingredient = Ingredient.objects.get(name=ingredient_data['name'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['quantity']
            )
