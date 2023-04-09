from django.contrib import admin

from .models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingList, Tag
)


class TagAdmin(admin.ModelAdmin):
    """Добавляет в панель администратора модель Tag"""
    list_display = ("name", "color", "slug")
    search_fields = ('name', 'slug',)


class IngredientAdmin(admin.ModelAdmin):
    """Добавляет в панель администратора модель Ingredient"""
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class IngredientInLine(admin.StackedInline):
    """Добавляет наборы ингредиентов для рецепта"""
    model = RecipeIngredient
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    """Добавляет в панель администратора модель Recipe"""
    list_display = ('author', 'name', 'favorite_count')
    list_filter = ('author', 'name', 'tags')
    inlines = [IngredientInLine]

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).distinct().count()

    favorite_count.short_description = 'Добавлено в избранное (раз)'


class ShoppingCartAdmin(admin.ModelAdmin):
    """Добавляет в панель администратора модель ShoppingCart"""
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe',)


class FavoriteAdmin(admin.ModelAdmin):
    """Добавляет в панель администратора модель Favorite"""
    list_display = ('recipe', 'user')
    list_filter = ('user',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingList, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
