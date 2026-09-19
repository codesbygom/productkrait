from django.db import models
from account.models import User
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.core.validators import MinValueValidator
from django.utils.text import slugify



class Category(models.Model):
    title    = models.CharField(max_length=200 , verbose_name="Category",)
    slug     = models.SlugField(max_length=200 , verbose_name="Slug", unique=True)
    status   = models.BooleanField(default=True , verbose_name="Show?",)
    position = models.IntegerField(verbose_name='Position')
    parent   = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='Parent category')

    class Meta:
        ordering = ['title',]
        verbose_name="Category"
        verbose_name_plural='Categories'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/{self.slug}/'

    def get_all_children(self):
        """Recursively fetch all descendant categories."""
        children = []
        for child in self.children.all():
            children.append(child)
            children.extend(child.get_all_children())
        return children

    def get_all_parents(self):
        """Recursively fetch all ancestor categories."""
        parents = []
        if self.parent:
            parents.append(self.parent)
            parents.extend(self.parent.get_all_parents())
        return parents

    def is_root(self):
        """Check whether this category is a root category."""
        return self.parent is None

    def get_level(self):
        """Get the category's depth level (0 for a root category)."""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level


class Product(models.Model):
    title          = models.CharField(max_length=200)
    slug           = models.SlugField()
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    category       = models.ManyToManyField(Category, related_name='products')
    description    = models.TextField(blank=True, null=True)
    price          = models.DecimalField(max_digits=10, decimal_places=2)
    image          = models.ImageField(upload_to="images")
    thumbnail      = models.ImageField(upload_to='uploads/', blank=True, null=True)
    date_added     = models.DateTimeField(auto_now_add=True)
    quantity       = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_added',]
        verbose_name="Product"
        verbose_name_plural='Products'

    def get_absolute_url(self):
        first_category = self.category.first()
        if first_category:
            return f'/{first_category.slug}/{self.slug}/'
        return f'/{self.slug}/'

    def get_thumbnail(self):
        if not self.thumbnail:
            self.thumbnail = self.make_thumbnail(self.image)
            self.save()
        return self.thumbnail.url

    def make_thumbnail(self, image, size=(300, 200)):
        img = Image.open(image).convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        return File(thumb_io, name=image.name)


class Cart(models.Model):
    user = models.ForeignKey(
        'account.User',
        on_delete=models.CASCADE,
        verbose_name='User',
        related_name='carts'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Last updated'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active'
    )

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_active'],
                condition=models.Q(is_active=True),
                name='unique_active_cart_per_user'
            )
        ]

    def save(self, *args, **kwargs):
        if self.is_active:
            Cart.objects.filter(user=self.user, is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Cart {self.user.email} - {self.created_at.strftime("%Y-%m-%d")}'

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        self.items.all().delete()

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Cart'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Product'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Quantity'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Unit price'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Added at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Last updated'
    )

    class Meta:
        verbose_name = 'Cart item'
        verbose_name_plural = 'Cart items'
        unique_together = ('cart', 'product')

    def __str__(self):
        return f'{self.product.title} - {self.quantity} pcs'

    @property
    def total_price(self):
        return self.price * self.quantity

    def increase_quantity(self, amount=1):
        self.quantity += amount
        self.save()

    def decrease_quantity(self, amount=1):
        if self.quantity > amount:
            self.quantity -= amount
            self.save()
        else:
            self.delete()

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Awaiting payment'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
        related_name='orders'
    )

    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null = True)

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Placed at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Last updated'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Order status'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Total price'
    )
    shipping_address = models.TextField(
        verbose_name='Shipping address'
    )
    tracking_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Shipping tracking code'
    )
    tracking_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Order tracking number'
    )

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.user.email} - {self.created_at.strftime("%Y-%m-%d")}'

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()
        super().save(*args, **kwargs)

    def generate_tracking_number(self):
        import random
        import string
        from datetime import datetime

        now = datetime.now()
        date_part = now.strftime('%y%m%d')

        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

        tracking_number = f'ORD-{date_part}-{random_part}'

        while Order.objects.filter(tracking_number=tracking_number).exists():
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            tracking_number = f'ORD-{date_part}-{random_part}'

        return tracking_number

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def get_total_price(self):
        return sum(item.total_price for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Order'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Product'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Quantity'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Unit price'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Order item'
        verbose_name_plural = 'Order items'
        unique_together = ('order', 'product')

    def __str__(self):
        return f'{self.product.title} - {self.quantity} pcs'

    @property
    def total_price(self):
        return self.price * self.quantity


class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Awaiting payment'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('online', 'Online payment'),
        ('cash', 'Cash on delivery'),
        ('bank_transfer', 'Bank transfer'),
        ('wallet', 'Wallet'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
        related_name='payments'
    )
    payment_number = models.CharField(
        max_length=100,
        verbose_name='Payment number'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Payment method'
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Amount paid',
        null=True,
        blank=True,
        default=0
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Payment status'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment {self.payment_number} - {self.user.email}'
