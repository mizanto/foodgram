import base64
import uuid

from django.core.files.base import ContentFile
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

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'author', 'name', 'text',
                  'image', 'cooking_time')


class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post
    data. It uses base64 for encoding and decoding the contents of the file.
    """
    def to_internal_value(self, data):
        """
        Decode the file and return an instance of 'ContentFile'.
        """
        if isinstance(data, str):
            if 'data:' in data and ';base64,' in data:
                _, data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')
            data = ContentFile(
                decoded_file, name=self.get_file_name(decoded_file))
        return super().to_internal_value(data)

    def get_file_name(self, decoded_file, length=12):
        file_name = str(uuid.uuid4())[:length]
        file_extension = self.get_file_extension(file_name, decoded_file)
        return f'{file_name}.{file_extension}'

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension


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
        data = super().validate(data)
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

        for tag in tags_data:
            RecipeTag.objects.create(recipe=recipe, tag=tag)

        for ingredient in ingredient_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    pk=ingredient['ingredient']['id']
                ),
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()

        tags_data = validated_data.get('tags')
        instance.recipetag_set.all().delete()
        for tag in tags_data:
            RecipeTag.objects.create(recipe=instance, tag=tag)

        ingredients_data = validated_data.get('ingredients')
        instance.recipeingredient_set.all().delete()
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=Ingredient.objects.get(
                    pk=ingredient['ingredient']['id']),
                amount=ingredient['amount']
            )
        return instance
