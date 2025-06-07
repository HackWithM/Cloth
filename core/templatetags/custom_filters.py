from django import template

register = template.Library()

@register.filter(name='split')
def split_string(value, arg):
    """
    Splits a string by the given argument.
    Usage: {{ some_string|split:"," }}
    """
    if value:
        return value.split(arg)
    return []

@register.filter(name='trim')
def trim_string(value):
    """
    Trims whitespace from a string.
    Usage: {{ some_string|trim }}
    """
    if isinstance(value, str):
        return value.strip()
    return value