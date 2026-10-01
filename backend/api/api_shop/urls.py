from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CartItemDetailView, CartItemsView, CartView, CategoryDetail, CategoryViewSet,
    LatestProductsList, OrderViewSet, ProductDetail, ProductViewSet, category_list, search,
)

router = DefaultRouter()
router.register('products', ProductViewSet, basename='api-product')
router.register('category', CategoryViewSet, basename='api-category')
router.register('orders', OrderViewSet, basename='api-order')

urlpatterns = [
    path('latest_products/', LatestProductsList.as_view(), name='api-latest-products'),
    path('search/', search, name='api-search'),
    path('categories/', category_list, name='api-categories'),
    path('cart/', CartView.as_view(), name='api-cart'),
    path('cart/items/', CartItemsView.as_view(), name='api-cart-items'),
    path('cart/items/<int:product_id>/', CartItemDetailView.as_view(), name='api-cart-item'),
    path('', include(router.urls)),
    # catch-all slug routes last so they don't swallow the ones above
    path('<slug:category_slug>/<slug:product_slug>/', ProductDetail.as_view(), name='api-product-by-slug'),
    path('<slug:category_slug>/', CategoryDetail.as_view(), name='api-category-by-slug'),
]
