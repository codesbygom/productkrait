from django.urls import path

from .views import CategoryDetail, LatestProductsList, ProductDetail, category_list, search

urlpatterns = [
    path('latest_products/', LatestProductsList.as_view()),
    path('search/', search),
    path('categories/', category_list),
    path('<slug:category_slug>/<slug:product_slug>/', ProductDetail.as_view()),
    path('<slug:category_slug>/', CategoryDetail.as_view()),
]
