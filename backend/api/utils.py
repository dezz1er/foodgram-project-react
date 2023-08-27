from django.db.models import Sum

from recipes.models import IngredientRecipe


def get_ingredients_for_download(user) -> str:
    ingredients = (
        IngredientRecipe.objects.filter(recipe__buylist__user=user)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(amount=Sum('amount'))
    )
    ingredient_list = ['Список покупок:', ]
    for ingredient in ingredients:
        line = (f'{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' — {ingredient["amount"]}')
        ingredient_list.append(line)
    response_content = '\n'.join(ingredient_list)
    return response_content
