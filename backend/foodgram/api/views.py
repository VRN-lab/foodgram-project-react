from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import OBJECTS_ON_THE_PAGE
from users.models import User
from .filters import RecipeFilter, SearchFilter
from recipes.models import (
    Favorite, Ingredient, Recipe,
    ShoppingList, Tag
)
from users.models import Subscribe
from .paginators import PageNumberPaginatorModified
from .permissions import AuthorOrReadOnly
from .serializers import (
    FavoriteSerializer, IngredientSerializer,
    RecipeCreateSerializer, RecipeListSerializer,
    ShoppingListSerializer, SubscribersSerializer,
    SubscribeSerializer, TagSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPaginatorModified

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        return RecipeCreateSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)


class FavoriteViewSet(APIView):
    def post(self, request, recipe_id):
        data = {
            'user': request.user.id,
            'recipe': recipe_id
        }
        serializer = FavoriteSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, recipe_id):
        favorite = get_object_or_404(
            Favorite, user=request.user,
            recipe__id=recipe_id
        )
        favorite.delete()
        return Response(
            'Рецепт успешно удален',
            status=status.HTTP_204_NO_CONTENT
        )


class SubscribeViewSet(APIView):
    def post(self, request, author_id=None):
        if author_id:
            data = {
                'user': request.user.id,
                'author': author_id
            }
            serializer = SubscribeSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)

    def get(self, request, author_id=None):
        user_obj = User.objects.filter(following__user=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = OBJECTS_ON_THE_PAGE
        result_page = paginator.paginate_queryset(user_obj, request)
        serializer = SubscribersSerializer(
            result_page, many=True, context={'current_user': request.user})
        return paginator.get_paginated_response(serializer.data)

    def delete(self, request, author_id=None):
        if author_id:
            subscribe = get_object_or_404(
                Subscribe, user=request.user,
                author__id=author_id
            )
            subscribe.delete()
            return Response(
                'Подписка успешно удалена',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ShoppingListViewSet(APIView):
    def post(self, request, recipe_id):
        data = {
            'user': request.user.id,
            'recipe': recipe_id
        }
        serializer = ShoppingListSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        shopping_list = get_object_or_404(
            ShoppingList, user=request.user,
            recipe__id=recipe_id
        )
        shopping_list.delete()
        return Response(
            'Рецепт успешно удален из списка покупок',
            status=status.HTTP_204_NO_CONTENT
        )


class DownloadShoppingCart(APIView):
    def get(self, request):
        shopping_cart = request.user.purchases.all()
        shopping_list = {}
        for purchase in shopping_cart:
            ingredients = purchase.recipe.recipeingredient_set.all()
            for ingredient in ingredients:
                name = ingredient.ingredient.name
                amount = ingredient.amount
                unit = ingredient.ingredient.measurement_unit
                if name not in shopping_list:
                    shopping_list[name] = {
                        'amount': amount,
                        'unit': unit
                    }
                else:
                    shopping_list[name]['amount'] = (shopping_list[name]
                                                     ['amount'] + amount)
        export = []
        for item in shopping_list:
            export.append(f'{item} ({shopping_list[item]["unit"]}) — '
                          f'{shopping_list[item]["amount"]} \n')
        response = HttpResponse(export, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="cart.txt"'
        return response
