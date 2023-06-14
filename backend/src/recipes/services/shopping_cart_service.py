from recipes.models import Recipe, RecipeIngredient


class ShoppingCartService:
    @staticmethod
    def get_ingredients(shopping_cart):
        ingredients = {}
        for item in shopping_cart:
            recipe = Recipe.objects.get(id=item.recipe.id)
            for ingredient in recipe.ingredients.all():
                recipe_ingredient = RecipeIngredient.objects.get(
                    recipe=recipe, ingredient=ingredient)
                amount = recipe_ingredient.amount
                if ingredient.name in ingredients:
                    ingredients[ingredient.name]['amount'] += amount
                else:
                    ingredients[ingredient.name] = {
                        'amount': amount,
                        'measurement_unit': ingredient.measurement_unit
                    }
        return ingredients
