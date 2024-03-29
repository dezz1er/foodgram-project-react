from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from .constants import (CHARS_MAX_LEN, HEX_COLOR_MAX_LEN,
                        MAX_AMOUNT_INGREDIENT, MAX_COOKING_TIME,
                        MEASUREMENT_UNIT_MAX_LEN, MIN_AMOUNT_INGREDIENT,
                        MIN_COOKING_TIME, RECIPE_NAME_MAX_LEN,
                        RECIPE_TEXT_MAX_LEN, STR_REPR_LEN)
from .validators import validate_hex_color

User = get_user_model()


class Ingredient(models.Model):

    name = models.CharField(
        max_length=CHARS_MAX_LEN,
        db_index=True,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_MAX_LEN,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id', 'name')
        constraints = [UniqueConstraint(
            fields=('name', 'measurement_unit'),
            name='unique_ingredient_measurement_units',
            violation_error_message='Запись ингредиент-ед._измерения уже есть.'
        )
        ]

    def __str__(self):
        return self.name[:STR_REPR_LEN]


class Tag(models.Model):

    name = models.CharField(
        max_length=CHARS_MAX_LEN,
        unique=True,
        db_index=True,
        verbose_name='Название'
    )
    color = models.CharField(
        validators=[validate_hex_color],
        max_length=HEX_COLOR_MAX_LEN,
        verbose_name='Цвет(HEX)'
    )
    slug = models.SlugField(
        max_length=CHARS_MAX_LEN,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('id', 'name')

    def __str__(self):
        return self.name[:STR_REPR_LEN]


class Recipe(models.Model):
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LEN,
        verbose_name='Название'
    )
    text = models.TextField(
        max_length=RECIPE_TEXT_MAX_LEN,
        verbose_name='Описание'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MaxValueValidator(MAX_COOKING_TIME,
                                      "Максимальное время - 1000 минут"),
                    MinValueValidator(MIN_COOKING_TIME,
                                      "Минимальное время - 1 минута")],
        verbose_name='Время приготовления (минуты)'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Фото'
    )
    tag = models.ManyToManyField(
        to=Tag,
        related_name='recipes',
        verbose_name='Теги',
        db_index=True,
    )
    ingredient = models.ManyToManyField(
        to=Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
        through='IngredientRecipe'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('-pub_date', 'id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:STR_REPR_LEN]


class IngredientRecipe(models.Model):

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    amount = models.PositiveIntegerField(
        validators=[MaxValueValidator(MAX_AMOUNT_INGREDIENT,
                                      "Максимальноe количество - 3000"),
                    MinValueValidator(MIN_AMOUNT_INGREDIENT,
                                      "Минимальное количество - 1")],
        verbose_name='Количество'
    )

    class Meta:
        ordering = ('recipe', 'id',)
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = [UniqueConstraint(
            fields=('recipe', 'ingredient'),
            name='unique_recipe_ingredient',
            violation_error_message='Этот ингредиент уже есть в рецепте.'
        )
        ]


class BaseUserRecipeRelation(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [UniqueConstraint(
            fields=('user', 'recipe'),
            name='unique_user_and_relation_recipe')]

    def __str__(self):
        return f'{self.user} и {self.recipe}'


class Favorite(BaseUserRecipeRelation):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [UniqueConstraint(
            fields=('user', 'recipe'),
            name='unique_user_and_favorite_recipe')]


class BuyList(BaseUserRecipeRelation):

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [UniqueConstraint(
            fields=('user', 'recipe'),
            name='unique_user_and_buylist_recipe')]
