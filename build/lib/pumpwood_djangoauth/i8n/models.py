"""Manage Kong routes for Pumpwood."""
from django.db import models
from pumpwood_djangoviews.action import action
from django.utils import timezone
from pumpwood_djangoauth.i8n.translate import t


class PumpwoodI8nTranslation(models.Model):
    """Model to perform I8n on Pumpwood."""

    sentence = models.TextField(
        null=False, unique=False,
        verbose_name=t(
            "Sentence",
            tag="PumpwoodI8nTranslation__admin__sentence"),
        help_text=t(
            "sentence for i8n.",
            tag="PumpwoodI8nTranslation__admin__sentence"))
    tag = models.CharField(
        max_length=154, null=False, unique=False, blank=True, default="",
        verbose_name=t(
            'Tag',
            tag="PumpwoodI8nTranslation__admin__tag"),
        help_text=t(
            "tag to differenciate same sentences, but different contexts",
            tag="PumpwoodI8nTranslation__admin__tag"))
    plural = models.BooleanField(
        null=False,
        verbose_name=t(
            'Is Plural?',
            tag="PumpwoodI8nTranslation__admin__plural"),
        help_text=t(
            "if sentence must be i8n on plural or not.",
            tag="PumpwoodI8nTranslation__admin__plural"))
    language = models.CharField(
        null=False, max_length=10, unique=False, blank=True,
        verbose_name=t(
            "Language",
            tag="PumpwoodI8nTranslation__admin__language"),
        help_text=t(
            "language of the corresponding i8n",
            tag="PumpwoodI8nTranslation__admin__language"))
    user_type = models.CharField(
        null=False, max_length=10, unique=False, blank=True, default="",
        verbose_name=t(
            "User type",
            tag="PumpwoodI8nTranslation__admin__user_type"),
        help_text="tag to diferenciate different user context")
    translation = models.TextField(
        null=True, unique=False, blank=True,
        verbose_name=t(
            "Translation",
            tag="PumpwoodI8nTranslation__admin__translation"),
        help_text=t(
            "sentence translation",
            tag="PumpwoodI8nTranslation__admin__translation"))
    do_not_remove = models.BooleanField(
        null=False,
        default=False,
        verbose_name=t(
            "Do not remove?",
            tag="PumpwoodI8nTranslation__admin__do_not_remove"),
        help_text=t(
            "Do not remove idle translation?",
            tag="PumpwoodI8nTranslation__admin__do_not_remove"))
    last_used_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name=t(
            'Last used at',
            tag="PumpwoodI8nTranslation__admin__last_used_at"),
        help_text=t(
            "Time translation was last used.",
            tag="PumpwoodI8nTranslation__admin__last_used_at"))

    def __str__(self):
        return '[%s] %s' % (self.id, self.sentence)

    class Meta:
        db_table = 'i8n__translation'
        verbose_name = t(
            'Pumpwood I8n Translation',
            tag="PumpwoodI8nTranslation__admin")
        verbose_name_plural = t(
            'Pumpwood I8n Translations',
            tag="PumpwoodI8nTranslation__admin", plural=True)
        unique_together = [[
            'sentence', 'tag', 'plural', 'language', 'user_type']]

    @classmethod
    @action(info=(
        'Translate sentence according to sentence/tag/plural/'
        'language/user_type.'))
    def translate(cls, sentence: str, tag: str = "",
                  plural: bool = False, language: str = "",
                  user_type: str = "") -> str:
        """
        Fetch sentence translation from database.

        Use sentence/tag/plural/language/user_type to locate a corresponding
        translation to the sentence. If not present on table a new entry
        will be generated.

        Args
            sentence [str]: Sentence to be translated.
        Kwargs:
            tag [str]: Tag used to differenciate same sentence, but with
                different contexts leading to different translations.
            plural [bool]: If sentence should be translated to plural,
                sentences without plural differences can be set as False as
                default.
            language [str]: Language to which translate the sentence. If
                not necessary multi language it can be set as empty string
                ''.
            user_type [str]: It is possible to have different translation
                depending of the user type. If not necessary can be set
                as empty string.
        Return [str | None]:
            Return the translated string. If no translation found, return
            same sentence.
        """
        translation_obj = cls.objects.filter(
            sentence=sentence, tag=tag, plural=plural, language=language,
            user_type=user_type).first()
        if translation_obj is None:
            translation_obj = cls(
                sentence=sentence, tag=tag, plural=plural,
                language=language, user_type=user_type)
            translation_obj.save()
        else:
            # Update once a day not to over request backend
            now_time = timezone.now()
            diff_timeused = now_time - translation_obj.last_used_at
            if 1 <= diff_timeused.days:
                translation_obj.last_used_at = now_time
        return translation_obj.translation or sentence
