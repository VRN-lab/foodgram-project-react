import re

from django.core.exceptions import ValidationError


def validate_alpha(value):
    if not re.match("^[a-zA-Zа-яА-Я]+$", value):
        raise ValidationError('Название должно состоять из букв')
