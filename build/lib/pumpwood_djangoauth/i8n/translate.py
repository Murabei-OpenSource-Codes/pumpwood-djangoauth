"""Create a class to make lazy translation of strings."""
import os
import datetime
from lazy_string import LazyString

# Translation cache to reduce backend calls
_translation_cache: dict = {}
_cache_expiry = float(os.getenv(
    "PUMPOOD__I8N__CACHE_EXPIRY", "1"))
CACHE_KEY_TEMPLATE: str = (
    "{sentence}||{tag}||{plural}||{language}||{user_type}")


def aux_translate_string(sentence, tag, plural, language, user_type) -> str:
    """
    Translate string using microservice.

    Cache results to reduce database calls.

    Args:
        sentence [str]: Sentence to be translated.
        tag [str]: Tag used in translation.
        plural [str]: If should be translated on plural.
        language [str]: Language to translate.
        user_type [str]: It is possible to set diferente types of user for
            translation.
    Return [str]:
        Return translated sentence.
    """
    if sentence is None:
        return None

    now_time = datetime.datetime.utcnow()
    cache_key = CACHE_KEY_TEMPLATE.format(
        sentence=sentence, tag=tag, plural=plural, language=language,
        user_type=user_type)
    cache_results = _translation_cache.get(cache_key, {})
    # Check if translation can be considered expired or is not set yet
    translation = cache_results.get("translation")
    expiry_time = cache_results.get(
        "expiry_time", datetime.datetime(1990, 1, 1))

    # Translation cache not set
    is_translation_none = translation is None
    # Translation expired
    is_translation_expired = expiry_time <= now_time
    if not is_translation_none and not is_translation_expired:
        # If not expired and not None translation will be returned
        # without calling backend
        return translation

    try:
        from pumpwood_djangoauth.i8n.models import PumpwoodI8nTranslation
        translation = PumpwoodI8nTranslation.translate(
            sentence=sentence, tag=tag, plural=plural,
            language=language, user_type=user_type)
    except Exception as e:
        print("aux_translate_string Exception:", str(e))
        return sentence

    expiry_time = now_time + datetime.timedelta(hours=_cache_expiry)
    _translation_cache[cache_key] = {
        "translation": translation, "expiry_time": expiry_time}
    return translation


def t(sentence, tag='', plural=False, language='', user_type=''):
    """Create a Lazy String to translate sentence when used."""
    return LazyString(
        aux_translate_string, sentence=sentence, tag=tag,
        plural=plural, language=language,
        user_type=user_type)
