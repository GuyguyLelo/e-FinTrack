from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def format_montant(value):
    """Formater un montant avec séparateurs de milliers"""
    if value:
        try:
            return intcomma(value)
        except (ValueError, TypeError):
            return value
    return "0"
