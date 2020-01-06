from django import template

register = template.Library()

@register.simple_tag
def translate(key, *args, **kwargs):
    from ..views import translate as tr
    return tr(key, *args, **kwargs)