from django import template

register = template.Library()

@register.filter
def get_item(obj, key):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, str(key), None)

@register.filter  
def get_attr(obj, attr):
    if obj is None:
        return None
    return getattr(obj, attr, None)