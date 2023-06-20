from rest_framework import serializers

from users.serializers import UserSerializer
from .fields import Base64ImageField
from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag


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
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeTagSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = RecipeTag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeRetriveSerializer(serializers.ModelSerializer):
    tags = RecipeTagSerializer(source='recipetag_set', many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'author', 'name', 'text',
                  'image', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.in_cart.filter(user=request.user).exists()
        return False


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = RecipeIngredientWriteSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'ingredients', 'tags', 'image',
                  'cooking_time')

    def validate(self, data):
        if len(data['tags']) != len(set(tag.id for tag in data['tags'])):
            raise serializers.ValidationError(
                {"tags": ["All tags must be unique."]})

        if len(data['ingredients']) != len(
            set(ingredient['ingredient']['id']
                for ingredient in data['ingredients'])
        ):
            raise serializers.ValidationError(
                {"ingredients": ["All ingredients must be unique."]})

        if len(data['tags']) == 0:
            raise serializers.ValidationError(
                {"tags": ["This field is required."]})
        if len(data['ingredients']) == 0:
            raise serializers.ValidationError(
                {"ingredients": ["This field is required."]})
        return data

    def to_representation(self, instance):
        self.fields['tags'] = TagSerializer(many=True)
        self.fields['ingredients'] = IngredientSerializer(many=True)
        self.fields['author'] = UserSerializer()
        representation = super().to_representation(instance)
        request = self.context.get('request')
        representation['image'] = request.build_absolute_uri(
            representation['image'])
        return representation

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredient_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self._create_recipe_tags(recipe, tags_data)
        self._create_recipe_ingredients(recipe, ingredient_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        instance = super().update(instance, validated_data)
        self._create_recipe_tags(instance, tags_data)
        self._create_recipe_ingredients(instance, ingredients_data)
        return instance

    def _create_recipe_tags(self, instance, tags_data):
        instance.recipetag_set.all().delete()
        if tags_data:
            RecipeTag.objects.bulk_create(
                [RecipeTag(recipe=instance, tag=tag) for tag in tags_data])

    def _create_recipe_ingredients(self, instance, ingredients_data):
        instance.recipeingredient_set.all().delete()
        if ingredients_data:
            RecipeIngredient.objects.bulk_create(
                [RecipeIngredient(
                    recipe=instance,
                    ingredient_id=ingredient['ingredient']['id'],
                    amount=ingredient['amount']
                ) for ingredient in ingredients_data]
            )


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
