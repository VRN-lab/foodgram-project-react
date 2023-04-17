# Generated by Django 3.2.9 on 2023-04-17 11:02

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_subscribe_subscribe_unique_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, validators=[django.core.validators.RegexValidator(message='Не допустимые символы в Имени', regex='^[A-Za-zА-Яа-я]*$')], verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, validators=[django.core.validators.RegexValidator(message='Не допустимые символы в Фамилии', regex='^[A-Za-zА-Яа-я]*$')], verbose_name='last name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Не допустимые символы в Имени пользователя', regex='^[A-Za-zА-Яа-я]*$')], verbose_name='Логин пользователя'),
        ),
    ]
