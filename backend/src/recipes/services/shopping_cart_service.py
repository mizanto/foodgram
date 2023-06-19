from django.db.models import Sum

from recipes.models import RecipeIngredient


class ShoppingCartService:
    @staticmethod
    def get_ingredients(shopping_cart):
        ingredients = {}
        recipe_ids = shopping_cart.values_list('recipe_id', flat=True)
        recipe_ingredients = (
            RecipeIngredient.objects
            .filter(recipe_id__in=recipe_ids)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )

        for ingredient in recipe_ingredients:
            ingredients[ingredient['ingredient__name']] = {
                'amount': ingredient['total_amount'],
                'measurement_unit': ingredient['ingredient__measurement_unit']
            }
        return ingredients
