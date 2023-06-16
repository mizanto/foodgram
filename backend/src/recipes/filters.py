from django_filters import rest_framework as filters

from .models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_by_shopping_cart')
    tags = filters.CharFilter(method='filter_by_tags')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorited_by__user=self.request.user)
        return queryset

    def filter_by_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(in_cart__user=self.request.user)
        return queryset

    def filter_by_tags(self, queryset, name, value):
        tag_slugs = self.request.query_params.getlist('tags')
        if tag_slugs:
            queryset = queryset.filter(tags__slug__in=tag_slugs).distinct()
        return queryset
