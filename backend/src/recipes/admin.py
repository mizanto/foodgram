from django.contrib import admin
from .models import (Favorite,
                     Ingredient,
                     Recipe,
                     RecipeIngredient,
                     RecipeTag,
                     Tag,)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'get_favorites_count')
    list_filter = ('author', 'name', 'tags')

    def get_favorites_count(self, obj):
        return obj.favorited_by.count()

    get_favorites_count.short_description = 'Number of favorites'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
admin.site.register(Favorite)
