from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter as BaseSearchFilter

from recipes.models import Recipe, Tag
from users.models import User


class RecipeFilter(filters.FilterSet):
    """
    Кастомный фильтр для корректного отображения
    Избранного и Корзины покупок
    """
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', queryset=Tag.objects.all(),
        to_field_name='slug'
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:

            return queryset.filter(favorited_by__user=self.request.user)

        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:

            return queryset.filter(customers__user=self.request.user)

        return queryset

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class SearchFilter(BaseSearchFilter):
    search_param = 'name'
