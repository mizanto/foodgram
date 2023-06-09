from rest_framework import mixins, viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend

from .models import Tag, Ingredient, Recipe
from .paginators import RecipePaginator
from .permissions import IsOwner
from .serializers import (TagSerializer,
                          IngredientSerializer,
                          RecipeCreateUpdateSerializer,
                          RecipeRetriveSerializer,)


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    pagination_class = RecipePaginator
    filterset_fields = ['author', 'tags']

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
        elif self.action == 'remove':
            print('remove')
            return None

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
