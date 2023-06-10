from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited']

    def filter_is_favorited(self, queryset, name, value):
        request = self.request
        if not request or not request.user.is_authenticated:
            return queryset
        if value:
            return queryset.filter(favorited_by__user=request.user)
        else:
            return queryset.exclude(favorited_by__user=request.user)
