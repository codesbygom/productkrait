from rest_framework import serializers

from shop.models import Category, Product


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


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = (
            'id',
            'title',
            'slug',
            'parent',
            'products',
        )
        read_only_fields = fields
