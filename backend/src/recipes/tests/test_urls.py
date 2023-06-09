import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import override_settings
from PIL import Image
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from rest_framework.views import status
from urllib.parse import urlparse
from io import BytesIO

from recipes.models import (Tag,
                            Ingredient,
                            Recipe,
                            RecipeIngredient)
from recipes.serializers import (TagSerializer,
                                 IngredientSerializer,
                                 RecipeRetriveSerializer,)
from users.models import User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEST_BASE64_IMAGE = """
    iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0e \
    cCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==
"""


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


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class RecipeListViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(
            email='user@user.co',
            username='user',
            password='1qa!QA1qa'
        )
        cls.test_token = Token.objects.create(user=cls.test_user)
        cls.tag = Tag.objects.create(
            name="breakfast", color="#E26C2D", slug="breakfast")
        cls.ingredient = Ingredient.objects.create(
            name="potato", measurement_unit="g")

        cls.image = Image.new('RGB', (1, 1))
        cls.image.save('test.jpg')

        for i in range(20):
            recipe = Recipe.objects.create(author=cls.test_user,
                                           name=f'recipe{i}',
                                           text='description',
                                           cooking_time=30)
            with open('test.jpg', 'rb') as f:
                recipe.image.save('test.jpg', f)
            recipe.tags.add(cls.tag)
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=cls.ingredient, amount=1)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = APIClient()
        self.authorized_client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.test_token.key)
        self.unauthorized_client = APIClient()

    def create_mock_recipe(self, author, name, text):
        with open('test.jpg', 'rb') as f:
            recipe = Recipe.objects.create(
                author=author,
                name=name,
                text=text,
                cooking_time=10,
                image=File(f, 'test.jpg')
            )
        return recipe

    def assertResponseMatchesSerializer(self, response_item, serializer_item):
        for key in response_item.keys():
            if key == 'image':
                self.assertEqual(
                    urlparse(response_item[key]).path,
                    urlparse(serializer_item[key]).path
                )
            else:
                self.assertEqual(response_item[key], serializer_item[key])

    def assertListResponseMatchesSerializer(self, response, serializer):
        response_data = response.data.get('results')
        serializer_data = serializer.data

        for response_item, serializer_item in zip(response_data,
                                                  serializer_data):
            self.assertResponseMatchesSerializer(
                response_item, serializer_item)

    def test_get_recipes_list_without_params(self):
        response = self.unauthorized_client.get(
            reverse('api:recipes:recipe-list'))
        recipes = Recipe.objects.all()
        serializer = RecipeRetriveSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListResponseMatchesSerializer(response, serializer)

    def test_get_recipes_list_with_pagination(self):
        response = self.unauthorized_client.get(
            reverse('api:recipes:recipe-list'), {"limit": 5, "page": 2})
        recipes = Recipe.objects.all()[5:10]
        serializer = RecipeRetriveSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListResponseMatchesSerializer(response, serializer)

    def test_get_recipes_list_with_tag_filter(self):
        response = self.unauthorized_client.get(
            reverse('api:recipes:recipe-list'), {"tags": 1})
        recipes = Recipe.objects.filter(tags__id=1)
        serializer = RecipeRetriveSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListResponseMatchesSerializer(response, serializer)

    def test_get_recipes_list_with_author_filter(self):
        response = self.unauthorized_client.get(
            reverse('api:recipes:recipe-list'), {"author": 1})
        recipes = Recipe.objects.filter(author__id=1)
        serializer = RecipeRetriveSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListResponseMatchesSerializer(response, serializer)

    def test_get_recipe_by_id(self):
        response = self.unauthorized_client.get(
            reverse('api:recipes:recipe-detail', kwargs={'pk': 1}))
        recipe = Recipe.objects.get(id=1)
        serializer = RecipeRetriveSerializer(recipe)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseMatchesSerializer(response.data, serializer.data)

    def generate_image_file(self):
        image = Image.new('RGB', (100, 100))
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        return SimpleUploadedFile(
            'test.jpg', image_io.read(), content_type='image/jpeg')

    def test_create_recipe(self):
        tag = Tag.objects.create(name='Tag1')
        ingredient = Ingredient.objects.create(name='Ingredient1')

        recipe_data = {
            'name': 'Recipe1',
            'text': 'Some text',
            'cooking_time': 10,
            'tags': [tag.id],
            'ingredients': [{'id': ingredient.id, 'amount': 2}],
            'image': f'data:image/png;base64, {TEST_BASE64_IMAGE}'
        }

        response = self.authorized_client.post(
            reverse('api:recipes:recipe-list'),
            data=recipe_data,
            format='json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data['image'])

    def test_create_recipe_with_empty_tags_and_ingredients(self):
        recipe_data = {
            'name': 'Recipe1',
            'text': 'Some text',
            'cooking_time': 10,
            'tags': [],
            'ingredients': [],
            'image': f'data:image/jpeg;base64, {TEST_BASE64_IMAGE}'
        }

        response = self.authorized_client.post(
            reverse('api:recipes:recipe-list'), data=recipe_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_recipe(self):
        tag = Tag.objects.create(name='Tag1')
        ingredient = Ingredient.objects.create(name='Ingredient1')

        recipe_data = {
            'name': 'Recipe1',
            'text': 'Some text',
            'cooking_time': 10,
            'tags': [tag.id],
            'ingredients': [{'id': ingredient.id, 'amount': 2}],
            'image': f'data:image/png;base64, {TEST_BASE64_IMAGE}'
        }

        response = self.authorized_client.post(
            reverse('api:recipes:recipe-list'),
            data=recipe_data,
            format='json'
        )

        recipe_id = response.data['id']

        recipe_data['name'] = 'Recipe2'
        recipe_data['text'] = 'Some text2'

        response = self.authorized_client.patch(
            reverse('api:recipes:recipe-detail', kwargs={'pk': recipe_id}),
            data=recipe_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_recipe(self):
        first_recipe = Recipe.objects.first()
        response = self.authorized_client.delete(
            reverse('api:recipes:recipe-detail',
                    kwargs={'pk': first_recipe.id})
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Recipe.objects.filter(id=first_recipe.id).exists())
