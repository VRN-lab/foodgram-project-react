from django.forms import ValidationError
from djoser.serializers import UserSerializer as BaseUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from users.models import User, Subscribe
from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingList, Tag
)


class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password',
        )


class UserShowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:

            return False

        return Subscribe.objects.filter(user=request.user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ShowRecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientToRecipeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = AddIngredientToRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'author', 'name', 'text', 'tags', 'ingredients',
            'image', 'pub_date', 'cooking_time',
        )
        read_only_fields = ('author',)

    def create_ingredient(self, recipe, ingredients):
        for ingredient in ingredients:
            obj = get_object_or_404(Ingredient, id=ingredient['id'])
            amount = ingredient['amount']
            RecipeIngredient.objects.bulk_create(
                [RecipeIngredient(
                    recipe=recipe,
                    ingredient=obj,
                    amount=amount,
                )]
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            image=image,
            **validated_data
        )
        recipe.tags.set(tags)
        ingredients = self.initial_data.get('ingredients')
        self.create_ingredient(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')

            for ingredient in ingredients:
                if ingredient['amount'] < 0:
                    raise serializers.ValidationError(
                        'Количество ингредиента не может быть меньше 1'
                    )
            instance.ingredients.clear()
            ingredients = self.initial_data.get('ingredients')
            self.create_ingredient(instance, ingredients)
        if 'tags' in self.initial_data:
            tags = validated_data.pop('tags')
            instance.tags.set(tags)

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        return instance

    def to_representation(self, instance):

        return RecipeListSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = {}
        for ingredient in ingredients:
            if ingredient.get('id') in ingredients_list:
                raise ValidationError(
                    ('Ингредиенты не должны повторяться')
                )
            if int(ingredient.get('amount')) <= 0:
                raise ValidationError(
                    ('Ингредиенты должны быть объемом/весом больше 0')
                )
            ingredients_list[ingredient.get('id')] = (
                ingredients_list.get('amount')
            )

        return data


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserShowSerializer()
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image',
            'text', 'cooking_time',
        )

    def get_ingredients(self, obj):
        qs = RecipeIngredient.objects.filter(recipe=obj)

        return ShowRecipeIngredientSerializer(qs, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:

            return False

        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:

            return False

        return ShoppingList.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('recipe', 'user',)

    def validate(self, attrs):
        request = self.context['request']
        if (request.method == 'GET' and Favorite.objects.filter(
            user=request.user,
            recipe=attrs['recipe']
        ).exists()):
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное'
            )

        return attrs

    def to_representation(self, instance):

        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = ('id', 'user', 'recipe', 'created_at',)

    def validate(self, attrs):
        request = self.context['request']
        if (request.method == 'GET' and ShoppingList.objects.filter(
            user=request.user,
            recipe=attrs['recipe']
        )):
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок'
            )

        return attrs

    def to_representation(self, instance):

        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class SubscribersSerializer(serializers.ModelSerializer):
    recipes = RecipeShortSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, obj):

        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:

            return False

        return Subscribe.objects.filter(user=obj, author=request.user).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('user', 'author',)

    def validate(self, attrs):
        request = self.context['request']
        if request.method == 'GET':
            if request.user == attrs['author']:
                raise serializers.ValidationError(
                    'Невозможно подписаться на себя'
                )
            if Subscribe.objects.filter(
                user=request.user,
                author=attrs['author']
            ).exists():
                raise serializers.ValidationError('Вы уже подписаны')

        return attrs

    def to_representation(self, instance):

        return SubscribersSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data
