from rest_framework import serializers

from shop.models import Cart, CartItem, Category, Order, OrderItem, Product


class ProductSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'slug',
            'url',
            'description',
            'price',
            'discount_price',
            'quantity',
            'image',
            'thumbnail',
        )
        read_only_fields = fields

    def get_thumbnail(self, obj):
        return obj.get_thumbnail() if obj.image else None


class ProductWriteSerializer(serializers.ModelSerializer):
    """Staff-only create/update of products."""
    category = serializers.SlugRelatedField(slug_field='slug', queryset=Category.objects.all(), many=True)

    class Meta:
        model = Product
        fields = ('id', 'title', 'slug', 'category', 'description', 'price', 'discount_price', 'quantity', 'image')

    def validate(self, data):
        price = data.get('price', getattr(self.instance, 'price', None))
        discount = data.get('discount_price', getattr(self.instance, 'discount_price', None))
        if discount is not None and price is not None and discount > price:
            raise serializers.ValidationError({'discount_price': 'Discount price cannot be higher than the price.'})
        return data

    def update(self, instance, validated_data):
        # A new image needs a new thumbnail; get_thumbnail() rebuilds it lazily.
        if 'image' in validated_data:
            instance.thumbnail = None
        return super().update(instance, validated_data)


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title', 'slug', 'parent', 'position')
        read_only_fields = fields


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    children = CategoryListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = (
            'id',
            'title',
            'slug',
            'parent',
            'children',
            'products',
        )
        read_only_fields = fields


class CategoryWriteSerializer(serializers.ModelSerializer):
    """Staff-only create/update of categories."""
    class Meta:
        model = Category
        fields = ('id', 'title', 'slug', 'status', 'position', 'parent')
        extra_kwargs = {'slug': {'required': False}}

    def validate_parent(self, parent):
        # a category can't be moved under itself or one of its own descendants
        if parent and self.instance and (parent == self.instance or parent in self.instance.get_all_children()):
            raise serializers.ValidationError('A category cannot be its own ancestor.')
        return parent


class CartItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'slug', 'price', 'quantity', 'image')
        read_only_fields = fields


class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity', 'price', 'total_price')
        read_only_fields = fields


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'total_price', 'updated_at')
        read_only_fields = fields


class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product')
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    # 0 removes the item, same as the web cart
    quantity = serializers.IntegerField(min_value=0)


class OrderItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price', 'total_price')
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'tracking_number', 'status', 'status_display', 'total_price',
            'shipping_address', 'tracking_code', 'items', 'created_at', 'updated_at',
        )
        read_only_fields = fields
