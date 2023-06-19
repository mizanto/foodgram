from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .paginators import RecipePaginator
from .permissions import IsOwner
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeRetriveSerializer, ShortRecipeSerializer,
                          TagSerializer)
from .services.shopping_cart_file_generator import FileGeneratorFactory
from .services.shopping_cart_service import ShoppingCartService


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            return queryset.filter(name__istartswith=name) | queryset.filter(
                name__icontains=name).exclude(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']
    pagination_class = RecipePaginator
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = RecipeFilter
    filterset_fields = ['author', 'tags', 'is_favorited']

    def get_permissions(self):
        if self.action in ['create', 'shopping_cart']:
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeRetriveSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        raise ValueError("Invalid action specified.")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='favorite')
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            return self._add_to_favorites(request, recipe)
        return self._remove_from_favorites(request, recipe)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'POST':
            return self._add_to_shopping_cart(request, recipe)
        return self._remove_from_shopping_cart(request, recipe)

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        format = self._get_format(request)

        shopping_cart = ShoppingCart.objects.filter(user=request.user)
        ingredients = ShoppingCartService.get_ingredients(shopping_cart)

        try:
            content, filename, content_type = (
                FileGeneratorFactory
                .get_generator(format)
                .generate(ingredients)
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    def _get_format(self, request):
        format = request.query_params.get('format')
        if format and format.lower() in ['txt', 'csv']:
            return format
        return 'txt'

    def _add_to_shopping_cart(self, request, recipe):
        _, created = ShoppingCart.objects.get_or_create(
            user=request.user, recipe=recipe)
        if created:
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"detail": "Recipe is already in shopping cart."},
                        status=status.HTTP_400_BAD_REQUEST)

    def _remove_from_shopping_cart(self, request, recipe):
        deleted_count, _ = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe).delete()
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Recipe is not in shopping cart."},
                        status=status.HTTP_400_BAD_REQUEST)

    def _add_to_favorites(self, request, recipe):
        _, created = Favorite.objects.get_or_create(
            user=request.user, recipe=recipe)
        if created:
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"detail": "Recipe is already in favorites."},
                        status=status.HTTP_400_BAD_REQUEST)

    def _remove_from_favorites(self, request, recipe):
        deleted_count, _ = Favorite.objects.filter(
            user=request.user, recipe=recipe).delete()
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Recipe is not in favorites."},
                        status=status.HTTP_400_BAD_REQUEST)
