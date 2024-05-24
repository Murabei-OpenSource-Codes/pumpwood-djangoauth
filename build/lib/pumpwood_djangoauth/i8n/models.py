"""Manage Kong routes for Pumpwood."""
from django.db import models
from pumpwood_djangoviews.action import action
from django.utils import timezone


class PumpwoodI8nTranslation(models.Model):
    """Model to perform I8n on Pumpwood."""

    sentence = models.TextField(
        null=False, unique=False,
        verbose_name="Sentence",
        help_text="sentence for i8n")
    tag = models.CharField(
        max_length=154, null=False, unique=False, blank=True, default="",
        verbose_name='Tag',
        help_text=(
            "tag to differenciate same sentences, but different contexts"))
    plural = models.BooleanField(
        null=False,
        verbose_name='Is Plural?',
        help_text="if sentence must be i8n on plural or not")
    language = models.CharField(
        null=False, max_length=10, unique=False, blank=True,
        verbose_name="Language",
        help_text="language of the corresponding i8n")
    user_type = models.CharField(
        null=False, max_length=10, unique=False, blank=True, default="",
        verbose_name="User type",
        help_text="tag to diferenciate different user context")
    translation = models.TextField(
        null=True, unique=False, blank=True,
        verbose_name="Translation",
        help_text="sentence translation")
    do_not_remove = models.BooleanField(
        null=False,
        default=False,
        verbose_name="Do not remove?",
        help_text="Do not remove idle translation?")
    last_used_at = models.DateTimeField(
        null=False, blank=True, auto_now=True,
        verbose_name='Last used at',
        help_text="Time translation was last used.")

    def __str__(self):
        return '[%s] %s' % (self.id, self.sentence)

    class Meta:
        db_table = 'i8n__translation'
        verbose_name = 'Pumpwood I8n Translation'
        verbose_name_plural = 'Pumpwood I8n Translations'
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
