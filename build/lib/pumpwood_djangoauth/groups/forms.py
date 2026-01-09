from django import forms
from flat_json_widget.widgets import FlatJsonWidget


class PumpwoodUserGroupAdminForm(forms.ModelForm):
    """Custom form for PumpwoodUserGroup model."""

    class Meta:
        """Meta."""
        widgets = {
            'dimensions': FlatJsonWidget,
            'extra_info': FlatJsonWidget
        }


class PumpwoodUserGroupM2MAdminForm(forms.ModelForm):
    """Custom form for PumpwoodUserGroupM2MAdmin model."""

    class Meta:
        """Meta."""
        widgets = {
            'extra_info': FlatJsonWidget
        }
