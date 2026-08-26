"""Extend Django Password validations."""
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class SpecialCharacterValidator:
    """Check if password has a special character."""

    def validate(self, password, user=None):
        """Require at least one non-alphanumeric character in the password.

        Args:
            password (str):
                Candidate password to validate.
            user:
                Django user instance; unused by this validator.

        Raises:
            ValidationError:
                When the password contains only alphanumeric characters.
        """
        has_special_char = any([not c.isalnum() for c in password])
        if not has_special_char:
            raise ValidationError(
                _("Sua senha precisa conter pelo menos um caracter especial."),
                code="no_special_character"
            )

    def get_help_text(self):
        """Return validator help text shown on password forms.

        Returns:
            str:
                Localized help message for password requirements.
        """
        return _("Sua senha precisa conter pelo menos um caracter especial")
