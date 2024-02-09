from django.core.management.commands.makemigrations import Command
from django.db import models

IGNORED_ATTRS = ['verbose_name', 'help_text', 'choices']

original_deconstruct = models.Field.deconstruct


def skip_i8n_fields_deconstruct(self):
    """Remove verbose_name, help_text and choices from migrations."""
    name, path, args, kwargs = original_deconstruct(self)
    print("skip_i8n_fields_deconstruct")
    for attr in IGNORED_ATTRS:
        kwargs.pop(attr, None)
    return name, path, args, kwargs
