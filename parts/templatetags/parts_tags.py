from django import template
from parts.models import Category

register = template.Library()

@register.simple_tag
def get_categories():
    """Get all active categories for use in templates"""
    return Category.objects.filter(is_active=True).order_by('name')
