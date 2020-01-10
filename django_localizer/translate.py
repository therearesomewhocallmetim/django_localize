from django.utils.translation import gettext, ngettext


def _get_n(*args, **kwargs):
    n = None
    if args:
        n = args[0]
    elif kwargs and len(kwargs) == 1:
        n = list(kwargs.items())[0][1]
    elif kwargs and 'n' in kwargs:
        n = kwargs['n']
    if isinstance(n, int):
        return n
    return None


def _get_str(key, n):
    if n is None:
        return gettext(key)
    return ngettext(key, key, n)


def translate(key, *args, **kwargs):
    n = _get_n(*args, **kwargs)
    s = _get_str(key, n)
    return s.format(*args, **kwargs)
