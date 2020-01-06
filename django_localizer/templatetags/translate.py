from django import template

register = template.Library()

@register.simple_tag
def translate(key, *args, **kwargs):
    from ..translate import translate as tr
    return tr(key, *args, **kwargs)
