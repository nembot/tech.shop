from .models import Category


def nav_categories(request):
    """Injecte la liste des catégories dans tous les templates (recherche navbar)."""
    return {"nav_categories": Category.objects.all().order_by("nom")}
