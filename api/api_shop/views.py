from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Category, Order, Product
from shop.repositories import CartRepository

from .serializers import (
    AddCartItemSerializer, CartSerializer, CategoryListSerializer, CategorySerializer,
    CategoryWriteSerializer, OrderSerializer, ProductSerializer, ProductWriteSerializer,
    UpdateCartItemSerializer,
)


class IsStaffOrReadOnly(permissions.BasePermission):
    """Anyone may read; only active staff (the same people allowed into
    /manage/) may create, edit or delete."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


def search_filter(query):
    return Q(title__icontains=query) | Q(description__icontains=query)


class LatestProductsList(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        products = Product.objects.all()[:5]
        return Response(ProductSerializer(products, many=True).data)


class ProductDetail(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, category_slug, product_slug, format=None):
        product = get_object_or_404(Product.objects.distinct(), category__slug=category_slug, slug=product_slug)
        return Response(ProductSerializer(product).data)


class CategoryDetail(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, category_slug, format=None):
        category = get_object_or_404(Category, slug=category_slug, status=True)
        return Response(CategorySerializer(category).data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def category_list(request, format=None):
    categories = Category.objects.filter(status=True)
    return Response(CategorySerializer(categories, many=True).data)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def search(request, format=None):
    """`GET ?query=...` or `POST {"query": ...}` (the original POST form is kept for existing clients)."""
    source = request.query_params if request.method == 'GET' else request.data
    query = source.get('query', '').strip()
    if not query:
        return Response([])
    return Response(ProductSerializer(Product.objects.filter(search_filter(query)), many=True).data)


class ProductViewSet(viewsets.ModelViewSet):
    """Products. Filters: `?category=<slug>`, `?search=<text>`,
    `?in_stock=true`, `?ordering=price|-price|date_added|-date_added|title`."""
    permission_classes = (IsStaffOrReadOnly,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    ORDERINGS = {'price', '-price', 'date_added', '-date_added', 'title', '-title'}

    def get_queryset(self):
        params = self.request.query_params
        qs = Product.objects.prefetch_related('category')

        query = params.get('search', '').strip()
        if query:
            qs = qs.filter(search_filter(query))
        category = params.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        if params.get('in_stock', '').lower() in ('1', 'true'):
            qs = qs.filter(quantity__gt=0)
        ordering = params.get('ordering')
        if ordering in self.ORDERINGS:
            qs = qs.order_by(ordering)
        return qs.distinct()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ProductWriteSerializer
        return ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """Categories, looked up by slug. Hidden ones (status=False) are only
    visible to staff. `?root=true` returns only top-level categories."""
    permission_classes = (IsStaffOrReadOnly,)
    lookup_field = 'slug'
    pagination_class = None

    def get_queryset(self):
        qs = Category.objects.all()
        if not self.request.user.is_staff:
            qs = qs.filter(status=True)
        if self.request.query_params.get('root', '').lower() in ('1', 'true'):
            qs = qs.filter(parent__isnull=True)
        return qs.order_by('position', 'title')

    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        if self.action == 'retrieve':
            return CategorySerializer
        return CategoryWriteSerializer


class CartView(APIView):
    """GET the active cart, DELETE empties it."""
    permission_classes = (permissions.IsAuthenticated,)
    cart_repository = CartRepository()

    def get(self, request):
        cart = self.cart_repository.get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data)

    def delete(self, request):
        cart = self.cart_repository.get_or_create_cart(request.user)
        self.cart_repository.clear_cart(cart)
        return Response(CartSerializer(cart).data)


class CartItemsView(generics.GenericAPIView):
    """POST {product_id, quantity} adds to the cart (quantities add up)."""
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AddCartItemSerializer
    cart_repository = CartRepository()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        with transaction.atomic():
            cart = self.cart_repository.get_or_create_cart(request.user)
            in_cart = cart.items.filter(product=product).values_list('quantity', flat=True).first() or 0
            if in_cart + quantity > product.quantity:
                return Response({'detail': 'Not enough stock available.', 'available': product.quantity},
                                status=status.HTTP_400_BAD_REQUEST)
            self.cart_repository.add_item(cart, product, quantity)

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(generics.GenericAPIView):
    """PATCH {quantity} sets the quantity (0 removes), DELETE removes the item."""
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UpdateCartItemSerializer
    cart_repository = CartRepository()

    def _cart_and_item(self, request, product_id):
        cart = self.cart_repository.get_or_create_cart(request.user)
        item = get_object_or_404(cart.items.select_related('product'), product_id=product_id)
        return cart, item

    def patch(self, request, product_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data['quantity']

        cart, item = self._cart_and_item(request, product_id)
        if quantity > item.product.quantity:
            return Response({'detail': 'Not enough stock available.', 'available': item.product.quantity},
                            status=status.HTTP_400_BAD_REQUEST)
        self.cart_repository.update_item_quantity(cart, product_id, quantity)
        return Response(CartSerializer(cart).data)

    put = patch

    def delete(self, request, product_id):
        cart, item = self._cart_and_item(request, product_id)
        self.cart_repository.remove_item(cart, product_id)
        return Response(CartSerializer(cart).data)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """The signed-in user's own orders. Orders are created through the
    payment gateway checkout, not through the API."""
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')
