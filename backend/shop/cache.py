"""Catalogue caching.

Every cached catalogue value is stored under the current "catalogue version".
Any change to a product or category (see shop/signals.py) bumps the version,
which makes all of those entries unreachable at once -- no need to track
which keys a given change affects. Old entries simply expire.

Works on any backend chosen with CACHE_BACKEND in settings (Redis, the file
cache on PythonAnywhere, LocMem, ...).
"""
from django.core.cache import cache

VERSION_KEY = 'catalog:version'
CATALOG_TIMEOUT = 60 * 15


def catalog_version():
    version = cache.get(VERSION_KEY)
    if version is None:
        cache.add(VERSION_KEY, 1, None)
        version = cache.get(VERSION_KEY, 1)
    return version


def bump_catalog_version():
    try:
        cache.incr(VERSION_KEY)
    except ValueError:  # key missing (evicted / never set)
        cache.set(VERSION_KEY, 2, None)


def cached_catalog(name, builder, timeout=CATALOG_TIMEOUT):
    """Return the cached value for `name`, building it with `builder()` on a miss."""
    key = f'catalog:v{catalog_version()}:{name}'
    value = cache.get(key)
    if value is None:
        value = builder()
        cache.set(key, value, timeout)
    return value


def get_category_tree():
    """Top-level active categories with their children prefetched (5 levels),
    as used by the navigation menu on every page."""
    from .models import Category

    def build():
        return list(
            Category.objects.filter(parent__isnull=True, status=True)
            .prefetch_related('children__children__children__children__children')
        )
    return cached_catalog('category-tree', build)


def get_active_categories():
    from .models import Category
    return cached_catalog('active-categories', lambda: list(Category.objects.filter(status=True)))
