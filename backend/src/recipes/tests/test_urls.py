from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.views import status

from recipes.models import Tag, Ingredient
from recipes.serializers import TagSerializer, IngredientSerializer


class TagTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_tag(name="", color="", slug=""):
        if name != "" and color != "" and slug != "":
            return Tag.objects.create(name=name, color=color, slug=slug)

    def setUp(self):
        self.create_tag("tag1", "#123456", "tag1")
        self.create_tag("tag2", "#654321", "tag2")

    def test_get_all_tags(self):
        response = self.client.get(
            reverse("api:recipes:tag-list")
        )
        expected = Tag.objects.all()
        serialized = TagSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_tag(self):
        response = self.client.get(
            reverse("api:recipes:tag-detail", kwargs={"pk": 1})
        )
        expected = Tag.objects.get(pk=1)
        serialized = TagSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class IngredientTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_ingredient(name="", measurement_unit=""):
        if name != "" and measurement_unit != "":
            return Ingredient.objects.create(
                name=name, measurement_unit=measurement_unit
            )

    def setUp(self):
        self.create_ingredient("ingredient1", "kg")
        self.create_ingredient("ingredient2", "g")

    def test_get_all_ingredients(self):
        response = self.client.get(
            reverse("api:recipes:ingredient-list")
        )
        expected = Ingredient.objects.all()
        serialized = IngredientSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_ingredient(self):
        response = self.client.get(
            reverse("api:recipes:ingredient-detail", kwargs={"pk": 1})
        )
        expected = Ingredient.objects.get(pk=1)
        serialized = IngredientSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
