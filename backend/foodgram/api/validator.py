import re

from django.core.exceptions import ValidationError


def validate_alpha(value):
    if re.match('^[\W\d]+$', value):
        raise ValidationError(
            'Название не должно состоять из какаих либо символов без букв'
        )
