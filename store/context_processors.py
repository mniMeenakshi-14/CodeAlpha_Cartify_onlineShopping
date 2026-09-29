from .cart import Cart


def cart_summary(request):
    """Makes {{ cart_item_count }} available in every template (navbar badge)."""
    return {"cart_item_count": len(Cart(request))}
