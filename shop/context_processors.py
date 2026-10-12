from .models import Category
from .services import get_active_cart

def active_cart(request):
    """Context processor to provide the active cart to all templates."""
    if request.user.is_authenticated:
        return {'active_cart': get_active_cart(request.user)}
    return {'active_cart': None}

def categories_tree(request):
    """Context processor to provide nested categories to all templates."""
    # Load all categories with their children recursively
    categories = Category.objects.active().roots().prefetch_related(
        'children__children__children__children__children'  # Support up to 5 levels
    )
    return {'categories_tree': categories}
