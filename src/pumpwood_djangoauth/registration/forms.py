from django import forms
from flat_json_widget.widgets import FlatJsonWidget


class UserProfileForm(forms.ModelForm):
    class Meta:
        widgets = {
            'dimensions': FlatJsonWidget,
            'extra_info': FlatJsonWidget
        }
