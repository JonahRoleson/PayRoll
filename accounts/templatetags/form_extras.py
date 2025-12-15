from django import template

register = template.Library()

@register.filter(name="add_class")
def add_class(field, css):
    """Inject a CSS class into a Django form widget in templates."""
    return field.as_widget(attrs={"class": css})
