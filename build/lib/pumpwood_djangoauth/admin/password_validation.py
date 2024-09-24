"""Extend Django Password validations."""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class SpecialCharacterValidator:
    def validate(self, password, user=None):
        has_special_char = any([not c.isalnum() for c in password])
        if not has_special_char:
            raise ValidationError(
                _("Sua senha precisa conter pelo menos um caracter especial."),
                code="no_special_character"
            )

    def get_help_text(self):
        return _("Sua senha precisa conter pelo menos um caracter especial")
