"""Create a class to make lazy translation of strings."""
from lazy_string import LazyString


def aux_translate_string(sentence, tag, plural, language, user_type):
    """Translate string using microservice."""
    from pumpwood_djangoauth.config import pumpwood_i8n
    return pumpwood_i8n.t(
        sentence=sentence, tag=tag, plural=plural,
        language=language, user_type=user_type)


def t(sentence, tag='', plural=False, language='', user_type=''):
    """Create a Lazy String to translate sentence when used."""
    return LazyString(
        aux_translate_string, sentence=sentence, tag=tag,
        plural=plural, language=language,
        user_type=user_type)
