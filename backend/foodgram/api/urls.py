from django.urls import include, path
from rest_framework import routers

from .views import (
    DownloadShoppingCart, FavoriteViewSet, IngredientViewSet,
    RecipeViewSet, ShoppingListViewSet, SubscribeViewSet,
    TagViewSet
)

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('users/subscriptions/',
         SubscribeViewSet.as_view(), name='users_subs'),
    path('users/<int:author_id>/subscribe/',
         SubscribeViewSet.as_view(), name='subscribe'),
    path('recipes/<int:recipe_id>/favorite/',
         FavoriteViewSet.as_view(), name='add_recipe_to_favorite'),
    path('recipes/<int:recipe_id>/shopping_cart/',
         ShoppingListViewSet.as_view(), name='shopping_cart'),
    path('recipes/download_shopping_cart/',
         DownloadShoppingCart.as_view(), name='download_shopping_cart'),
    path('', include(router.urls)),
]
