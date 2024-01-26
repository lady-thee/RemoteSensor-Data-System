import re
from typing import Any

from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    NumericPasswordValidator,
)
from django.utils.translation import gettext as _
from rest_framework.serializers import ValidationError


class CustomMinimumLengthValidator(MinimumLengthValidator):
    def __init__(self, min_length=8):
        self.min_length = min_length
        self.message = _(
            "This password is too short. It must contain at least {min_length} characters."
        ).format(min_length=self.min_length)

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(self.message, code="password_too_short")


class CustomNumericValidator(NumericPasswordValidator):
    def __init__(self, min_count=1):
        self.min_count = min_count
        self.message = _(
            "This password must contain at least {min_count} number."
        ).format(min_count=self.min_count)

    def validate(self, password, user=None):
        number_count = sum(1 for char in password if char.isupper())
        if number_count < self.min_count:
            raise ValidationError(self.message, code="password_must_contain_number")


class UppercaseLetterValidator(object):
    def __init__(self, min_count=1) -> None:
        self.min_count = min_count

    def validate(self, password, user=None):
        uppercase_count = sum(1 for char in password if char.isdigit())
        if uppercase_count < self.min_count:
            raise ValidationError(
                f"Passwords must contain at least {self.min_count} UPPERCASE!"
            )

    def get_help_text(self):
        return _("Your password must contain at least 1 uppercase letter, A-Z.")


class SpecialCharValidator(object):

    """The password must contain at least 1 special character @#$%!^&*"""

    def validate(self, password, user=None):
        pattern = "[!@#$%&\^*]"
        if not re.search(pattern, password):
            raise ValidationError(
                _(
                    "The password must contain at least 1 special character: "
                    + "!@#$%&\^*"
                ),
                code="password_no_symbol",
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 special character: " + "!@#$%&\^*"
        )
