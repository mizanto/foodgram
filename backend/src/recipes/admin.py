from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag, User


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'get_favorites_count')
    list_filter = ('author', 'title', 'tags')

    def get_favorites_count(self, obj):
        return obj.favorites.count()

    get_favorites_count.short_description = 'Number of favorites'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('email', 'username')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
