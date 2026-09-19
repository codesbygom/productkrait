from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Category, Product

from .serializers import CategorySerializer, ProductSerializer


class LatestProductsList(APIView):
    def get(self, request, format=None):
        products = Product.objects.all()[:5]
        return Response(ProductSerializer(products, many=True).data)


class ProductDetail(APIView):
    def get(self, request, category_slug, product_slug, format=None):
        product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
        return Response(ProductSerializer(product).data)


class CategoryDetail(APIView):
    def get(self, request, category_slug, format=None):
        category = get_object_or_404(Category, slug=category_slug)
        return Response(CategorySerializer(category).data)


@api_view(['GET'])
def category_list(request, format=None):
    categories = Category.objects.filter(status=True)
    return Response(CategorySerializer(categories, many=True).data)


@api_view(['POST'])
def search(request, format=None):
    query = request.data.get('query', '')
    if not query:
        return Response([])
    products = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    return Response(ProductSerializer(products, many=True).data)
