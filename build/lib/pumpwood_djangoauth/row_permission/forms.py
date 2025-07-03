from django import forms
from flat_json_widget.widgets import FlatJsonWidget


class PumpwoodRowPermissionAdminForm(forms.ModelForm):
    """Custom form for Pumpwood Permission Policy model."""

    class Meta:
        """Meta."""
        widgets = {
            'dimensions': FlatJsonWidget,
            'extra_info': FlatJsonWidget
        }
