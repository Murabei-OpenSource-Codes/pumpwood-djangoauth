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


class PumpwoodRowPermissionGroupM2MAdminForm(forms.ModelForm):
    """Custom form for Pumpwood Row Permission Group M2M Policy model."""

    class Meta:
        """Meta."""
        widgets = {
            'extra_info': FlatJsonWidget
        }


class PumpwoodRowPermissionUserM2MAdminForm(forms.ModelForm):
    """Custom form for Pumpwood Row PermissionUser M2M Policy model."""

    class Meta:
        """Meta."""
        widgets = {
            'extra_info': FlatJsonWidget
        }
