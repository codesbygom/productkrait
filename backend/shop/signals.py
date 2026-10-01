"""Invalidate the catalogue cache (shop/cache.py) whenever it changes."""
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .cache import bump_catalog_version
from .models import Category, Product


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def catalog_changed(sender, **kwargs):
    bump_catalog_version()


@receiver(m2m_changed, sender=Product.category.through)
def product_categories_changed(sender, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        bump_catalog_version()
