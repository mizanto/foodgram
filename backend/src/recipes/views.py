from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .filters import RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .paginators import RecipePaginator
from .permissions import IsOwner
from .serializers import (ShortRecipeSerializer,
                          IngredientSerializer,
                          RecipeCreateUpdateSerializer,
                          RecipeRetriveSerializer,
                          TagSerializer,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'head', 'options', 'patch', 'delete']
    pagination_class = RecipePaginator
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = RecipeFilter
    filterset_fields = ['author', 'tags', 'is_favorited']

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeRetriveSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer

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
        elif request.method == 'DELETE':
            return self._remove_from_favorites(request, recipe)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated],
            url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)

        recipe = self.get_object()
        if request.method == 'POST':
            return self._add_to_shopping_cart(request, recipe)
        elif request.method == 'DELETE':
            return self._remove_from_shopping_cart(request, recipe)

    def _add_to_shopping_cart(self, request, recipe):
        _, created = ShoppingCart.objects.get_or_create(
            user=request.user, recipe=recipe)
        if created:
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Recipe is already in shopping cart."},
                            status=status.HTTP_400_BAD_REQUEST)

    def _remove_from_shopping_cart(self, request, recipe):
        deleted_count, _ = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe).delete()
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Recipe is not in shopping cart."},
                            status=status.HTTP_400_BAD_REQUEST)

    def _add_to_favorites(self, request, recipe):
        _, created = Favorite.objects.get_or_create(
            user=request.user, recipe=recipe)
        if created:
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Recipe is already in favorites."},
                            status=status.HTTP_400_BAD_REQUEST)

    def _remove_from_favorites(self, request, recipe):
        deleted_count, _ = Favorite.objects.filter(
            user=request.user, recipe=recipe).delete()
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Recipe is not in favorites."},
                            status=status.HTTP_400_BAD_REQUEST)
