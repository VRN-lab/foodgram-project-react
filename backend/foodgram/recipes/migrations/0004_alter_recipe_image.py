# Generated by Django 4.2 on 2023-04-09 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_ingredient_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, help_text='Загрузите изображение', null=True, upload_to='media/recipes/images/', verbose_name='Изображение'),
        ),
    ]
