from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """
    A model that represents a tag.

    Fields:
    - name: The name of the tag.
    - color: The color of the tag in HEX format.
    - slug: The slug of the tag.
    """
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """
    A model that represents an ingredient.

    Fields:
    - name: The name of the ingredient.
    - measurement_unit: The unit of measurement for the ingredient.
    """
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    A model that represents a recipe.

    Fields:
    - author: The user who created this recipe.
    - title: The title of the recipe.
    - image: An image of the finished dish.
    - description: A description of the recipe.
    - ingredients: The ingredients used in the recipe.
    - tags: The tags associated with the recipe.
    - cooking_time: The cooking time for the recipe, in minutes.
    """
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/')
    description = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient')
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    cooking_time = models.IntegerField()

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    """
    A model that represents an ingredient used in a recipe.

    Fields:
    - recipe: The recipe that this ingredient is used in.
    - ingredient: The ingredient used in the recipe.
    - quantity: The quantity of the ingredient used in the recipe.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()

    def __str__(self):
        return f'{self.ingredient.name} for {self.recipe.title}'


class RecipeTag(models.Model):
    """
    A model that represents a tag associated with a recipe.

    Fields:
    - recipe: The recipe associated with this tag.
    - tag: The tag associated with this recipe.
    """
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        help_text='The recipe associated with this tag.')
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE,
        help_text='The tag associated with this recipe.')

    def __str__(self):
        return f'{self.recipe.title} - {self.tag.name}'
