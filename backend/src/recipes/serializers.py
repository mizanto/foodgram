from rest_framework import serializers

from .models import Tag, Ingredient, Recipe, RecipeIngredient, RecipeTag
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'quantity')


class RecipeTagSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = RecipeTag
        fields = ('id', 'name', 'color', 'slug')


class RecipeListSerializer(serializers.ModelSerializer):
    tags = RecipeTagSerializer(source='recipetag_set', many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')


class RecipeDetailSerializer(serializers.ModelSerializer):
    tags = RecipeTagSerializer(source='recipetag_set', many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True)
    tags = RecipeTagSerializer(source='recipetag_set', many=True)

    class Meta:
        model = Recipe
        fields = ['ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipeingredient_set')
        tags_data = validated_data.pop('recipetag_set')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **ingredient_data)
        for tag_data in tags_data:
            RecipeTag.objects.create(recipe=recipe, **tag_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipeingredient_set')
        tags_data = validated_data.pop('recipetag_set')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('ingredient').id
            ingredient = RecipeIngredient.objects.get(id=ingredient_id)
            ingredient.quantity = ingredient_data.get(
                'quantity', ingredient.quantity)
            ingredient.save()

        for tag_data in tags_data:
            tag_id = tag_data.get('tag').id
            tag = RecipeTag.objects.get(id=tag_id)
            tag.save()
        return instance
