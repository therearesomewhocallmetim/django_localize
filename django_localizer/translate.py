from django.utils.translation import gettext, ngettext


def _get_n(*args, **kwargs):
    if args:
        return args[0]
    elif kwargs and len(kwargs) == 1:
        return list(kwargs.items())[0][1]
    elif kwargs and 'n' in kwargs:
        return kwargs['n']
    return None


def _get_str(key, n):
    if n is None:
        return gettext(key)
    s = gettext(key)
    if s == key:
        return ngettext(key, key, n)
    return s


def translate(key, *args, **kwargs):
    n = _get_n(*args, **kwargs)
    s = _get_str(key, n)
    return s.format(*args, **kwargs)
