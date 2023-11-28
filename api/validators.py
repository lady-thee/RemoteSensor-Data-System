import re
from typing import Any

from django.utils.translation import gettext as _
from rest_framework.serializers import ValidationError


class UppercaseLetterValidator(object):
    def __init__(self, min_count=1) -> None:
        self.min_count = min_count

    def validate(self, password, user=None):
        uppercase_count = sum(1 for char in password if char.isupper())
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
