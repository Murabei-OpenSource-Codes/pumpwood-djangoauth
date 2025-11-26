from django import forms
from flat_json_widget.widgets import FlatJsonWidget


class PumpwoodPermissionPolicyAdminForm(forms.ModelForm):
    """Custom form for Pumpwood Permission Policy model."""

    class Meta:
        """Meta."""
        widgets = {
            'dimensions': FlatJsonWidget,
            'extra_info': FlatJsonWidget
        }


class PumpwoodPermissionPolicyActionAdminForm(forms.ModelForm):
    """Custom form for Pumpwood Permission Policy Action model."""

    class Meta:
        """Meta."""
        widgets = {
            'extra_info': FlatJsonWidget
        }


class PumpwoodPermissionPolicyGroupM2MAdminForm(forms.ModelForm):
    """Custom form for Pumpwood Permission Policy Group M2M Action."""

    class Meta:
        """Meta."""
        widgets = {
            'extra_info': FlatJsonWidget
        }


class PumpwoodPermissionPolicyUserM2MAdminForm(forms.ModelForm):
    """Custom form for Pumpwood Permission Policy Group M2M Action."""

    class Meta:
        """Meta."""
        widgets = {
            'extra_info': FlatJsonWidget
        }
