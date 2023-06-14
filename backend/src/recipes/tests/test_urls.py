import os
import shutil
import tempfile
from urllib.parse import urlencode, urlparse

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory, APITestCase
from rest_framework.views import status

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from recipes.serializers import (IngredientSerializer, RecipeRetriveSerializer,
                                 TagSerializer)
from users.models import User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEST_IMAGE_PATH = os.path.join(TEMP_MEDIA_ROOT, 'test.jpg')
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
        self.tag1 = self.create_tag("tag1", "#123456", "tag1")
        self.tag2 = self.create_tag("tag2", "#654321", "tag2")

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
            reverse("api:recipes:tag-detail",
                    kwargs={"pk": self.tag1.pk})
        )
        expected = Tag.objects.get(pk=self.tag1.pk)
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
        self.ingredient1 = self.create_ingredient("ingredient1", "kg")
        self.ingredient2 = self.create_ingredient("ingredient2", "g")

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
            reverse("api:recipes:ingredient-detail",
                    kwargs={"pk": self.ingredient1.pk})
        )
        expected = Ingredient.objects.get(pk=self.ingredient1.pk)
        serialized = IngredientSerializer(expected)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_ingredients(self):
        response = self.client.get(
            reverse("api:recipes:ingredient-list"), {'name': 'ingredient'}
        )
        startswith_expected = Ingredient.objects.filter(
            name__istartswith='ingredient')
        contains_expected = Ingredient.objects.filter(
            name__icontains='ingredient').exclude(
            name__istartswith='ingredient')
        expected = list(startswith_expected) + list(contains_expected)
        serialized = IngredientSerializer(expected, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class RecipeListViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user, cls.test_token = cls._create_test_user()
        cls.tag = Tag.objects.create(
            name="breakfast", color="#E26C2D", slug="breakfast")
        cls.ingredient = Ingredient.objects.create(
            name="potato", measurement_unit="g")
        cls.image = cls._create_test_image()
        cls.recipe = cls._create_test_recipe()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    @staticmethod
    def _create_test_user(email='user@user.co',
                          username='user',
                          password='1qa!QA1qa'):
        test_user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
        )
        test_token = Token.objects.create(user=test_user)
        return test_user, test_token

    @staticmethod
    def _create_test_image():
        image = Image.new('RGB', (1, 1))
        image.save(TEST_IMAGE_PATH)
        return image

    @classmethod
    def _create_test_recipe(cls, name='recipe'):
        recipe = Recipe.objects.create(author=cls.test_user,
                                       name=name,
                                       text='description',
                                       cooking_time=1)
        with open(TEST_IMAGE_PATH, 'rb') as f:
            recipe.image.save('test.jpg', f)
        recipe.tags.add(cls.tag)
        RecipeIngredient.objects.create(
            recipe=recipe, ingredient=cls.ingredient, amount=1)
        return recipe

    @classmethod
    def _create_test_recipes(cls, count=20):
        for i in range(count):
            cls._create_test_recipe(f'recipe{i}')

    @classmethod
    def _create_authorized_client(cls):
        authorized_client = APIClient()
        authorized_client.credentials(
            HTTP_AUTHORIZATION='Token ' + cls.test_token.key)
        return authorized_client

    def setUp(self):
        self.authorized_client = self._create_authorized_client()
        self.unauthorized_client = APIClient()

    def _test_get_recipes_list(self, params=None, recipes_slice=slice(None)):
        self._create_test_recipes()
        params = params or {}
        response = self.unauthorized_client.get(
            reverse('api:recipes:recipe-list'), params)
        recipes = Recipe.objects.all()[recipes_slice]
        self._assert_response_list(response, recipes)

    def _assert_response_list(self, response, recipes):
        serializer = RecipeRetriveSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListResponseMatchesSerializer(response, serializer)

    def test_get_recipes_list_without_params(self):
        self._test_get_recipes_list()

    def test_get_recipes_list_with_pagination(self):
        self._test_get_recipes_list({"limit": 5, "page": 2}, slice(5, 10))

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

    def test_get_recipes_list_with_tag_filter(self):
        response = self.unauthorized_client.get(
            reverse('api:recipes:recipe-list'), {"tags": self.tag.id})
        recipes = Recipe.objects.filter(tags__id=1)
        serializer = RecipeRetriveSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListResponseMatchesSerializer(response, serializer)

    def test_get_recipes_list_with_author_filter(self):
        response = self.unauthorized_client.get(
            reverse('api:recipes:recipe-list'), {"author": self.test_user.id})
        recipes = Recipe.objects.filter(author__id=1)
        serializer = RecipeRetriveSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListResponseMatchesSerializer(response, serializer)

    def test_get_recipes_list_with_is_favorited_filter(self):
        Favorite.objects.create(
            user=self.test_user, recipe=self.recipe)

        response = self.authorized_client.get(
            reverse('api:recipes:recipe-list'), {"is_favorited": True}
        )
        recipes = Recipe.objects.filter(favorited_by__user=self.test_user)

        factory = APIRequestFactory()
        request = factory.get(reverse('api:recipes:recipe-list'))
        request.user = self.test_user
        serializer = RecipeRetriveSerializer(
            recipes, many=True, context={'request': request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListResponseMatchesSerializer(response, serializer)

    def test_get_recipes_list_with_multiple_tags_filter(self):
        tag1 = Tag.objects.create(name="lunch", color="#E16B8C", slug="lunch")
        tag2 = Tag.objects.create(
            name="dinner", color="#884898", slug="dinner")

        self.recipe.tags.add(tag1, tag2)

        tag_slugs = [tag1.slug, tag2.slug]
        url_params = urlencode(
            [('tags', slug) for slug in tag_slugs], doseq=True)
        response = self.unauthorized_client.get(
            f"{reverse('api:recipes:recipe-list')}?{url_params}")
        recipes = Recipe.objects.filter(tags__slug__in=tag_slugs)
        serializer = RecipeRetriveSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListResponseMatchesSerializer(response, serializer)

    def test_get_recipe_by_id(self):
        response = self.unauthorized_client.get(
            reverse('api:recipes:recipe-detail',
                    kwargs={'pk': self.recipe.id}))
        recipe = Recipe.objects.get(id=1)
        serializer = RecipeRetriveSerializer(recipe)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertResponseMatchesSerializer(response.data, serializer.data)

    def test_create_recipe(self):
        recipe_data = {
            'name': 'Recipe1',
            'text': 'Some text',
            'cooking_time': 10,
            'tags': [self.tag.id],
            'ingredients': [{'id': self.ingredient.id, 'amount': 2}],
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
        upd_tag = Tag.objects.create(name='UpdTag')
        upd_ingredient = Ingredient.objects.create(name='UpdIngredient')

        recipe_data = {
            'name': 'Upd Name',
            'text': 'Upd text',
            'cooking_time': 100,
            'tags': [upd_tag.id],
            'ingredients': [{'id': upd_ingredient.id, 'amount': 2}],
            'image': f'data:image/png;base64, {TEST_BASE64_IMAGE}'
        }

        response = self.authorized_client.patch(
            reverse('api:recipes:recipe-detail',
                    kwargs={'pk': self.recipe.id}),
            data=recipe_data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_recipe(self):
        id_to_delete = self.recipe.id
        response = self.authorized_client.delete(
            reverse('api:recipes:recipe-detail',
                    kwargs={'pk': id_to_delete})
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Recipe.objects.filter(id=id_to_delete).exists())

    def test_add_to_favorites(self):
        response = self.authorized_client.post(
            reverse('api:recipes:recipe-favorite',
                    kwargs={'pk': self.recipe.id})
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Favorite.objects.filter(user=self.test_user,
                                                recipe=self.recipe).exists())

    def test_remove_from_favorites(self):
        Favorite.objects.create(user=self.test_user, recipe=self.recipe)
        response = self.authorized_client.delete(
            reverse('api:recipes:recipe-favorite',
                    kwargs={'pk': self.recipe.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Favorite.objects.filter(user=self.test_user,
                                                 recipe=self.recipe).exists())

    def test_add_to_favorites_twice(self):
        Favorite.objects.create(user=self.test_user, recipe=self.recipe)
        response = self.authorized_client.post(
            reverse('api:recipes:recipe-favorite',
                    kwargs={'pk': self.recipe.id})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_from_favorites_not_existed(self):
        response = self.authorized_client.delete(
            reverse('api:recipes:recipe-favorite',
                    kwargs={'pk': self.recipe.id})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_recipe_to_shopping_cart(self):
        response = self.authorized_client.post(
            reverse('api:recipes:recipe-shopping-cart',
                    kwargs={'pk': self.recipe.id})
        )
        query_set = ShoppingCart.objects.filter(
            user=self.test_user, recipe=self.recipe)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(query_set.exists())

    def test_add_recipe_to_shopping_cart_unauthenticated(self):
        response = self.unauthorized_client.post(
            reverse('api:recipes:recipe-shopping-cart',
                    kwargs={'pk': self.recipe.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_remove_recipe_from_shopping_cart(self):
        ShoppingCart.objects.create(user=self.test_user, recipe=self.recipe)
        response = self.authorized_client.delete(
            reverse('api:recipes:recipe-shopping-cart',
                    kwargs={'pk': self.recipe.id})
        )
        query_set = ShoppingCart.objects.filter(
            user=self.test_user, recipe=self.recipe)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(query_set.exists())

    def test_remove_recipe_from_shopping_cart_not_existed(self):
        response = self.authorized_client.delete(
            reverse('api:recipes:recipe-shopping-cart',
                    kwargs={'pk': self.recipe.id})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_recipe_from_shopping_cart_unauthenticated(self):
        response = self.unauthorized_client.delete(
            reverse('api:recipes:recipe-shopping-cart',
                    kwargs={'pk': self.recipe.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_recipe_to_shopping_cart_twice(self):
        ShoppingCart.objects.create(user=self.test_user, recipe=self.recipe)
        response = self.authorized_client.post(
            reverse('api:recipes:recipe-shopping-cart',
                    kwargs={'pk': self.recipe.id})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_download_shopping_cart(self):
        ShoppingCart.objects.create(user=self.test_user, recipe=self.recipe)
        response = self.authorized_client.get(
            reverse('api:recipes:recipe-download-shopping-cart')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.content)
        self.assertTrue(len(response.content) > 0)
