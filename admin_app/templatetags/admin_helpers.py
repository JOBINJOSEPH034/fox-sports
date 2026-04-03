from django import template

register = template.Library()

@register.simple_tag
def render_value(value):
    """
    Renders the value as a string.
    Bypasses standard {{ variable }} rendering issues by using a tag.
    """
    if value is None:
        return ""
    return str(value)
