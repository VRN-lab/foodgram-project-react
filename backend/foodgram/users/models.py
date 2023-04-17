from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Создает кастомную модель пользователей"""
    email = models.EmailField(unique=True,)
    username = models.CharField(
        ('Логин пользователя'), unique=True, max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zА-Яа-я]*$',
                message='Не допустимые символы в Имени пользователя'
            )
        ]
    )
    first_name = models.CharField(
        ('first name'), max_length=150, blank=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zА-Яа-я]*$',
                message='Не допустимые символы в Имени'
            )
        ]
    )
    last_name = models.CharField(
        ('last name'), max_length=150, blank=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zА-Яа-я]*$',
                message='Не допустимые символы в Фамилии'
            )
        ]
    )
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ('username', )
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        models.UniqueConstraint(
            fields=('username', 'email',), name='unique_value')

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Создает модель Подписки"""
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
