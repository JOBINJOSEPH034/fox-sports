
from django.db import models
from admin_app.models import Product, ProductVariant,Coupon,Offer
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Q
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError




#for user cart 
class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)  
    applied_coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 

     
    def update_total_price(self):
       
        cart_total = sum(item.total_price for item in self.cartitem_set.all())

        # Apply coupon discount
        if self.applied_coupon:
            discount = (cart_total * self.applied_coupon.discount_percentage) / 100
            cart_total -= discount

        self.total_price = cart_total
        self.save()


    def __str__(self):
        return f"Cart of {self.user.username}"

#for user cartitems 
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)
 
 
    @property
    def total_price(self):            #Calculate total price considering product/variant price and quantity.

       
        base_price = self.product.price + (self.variant.additional_price if self.variant else 0)
        discounted_price = self.get_discounted_price()
        return discounted_price * self.quantity
    
    def get_discounted_price(self):    # Return the discounted price if an offer exists.
       
        base_price = self.product.price + (self.variant.additional_price if self.variant else 0)
        applicable_offer = Offer.objects.filter(
            (Q(products=self.product) | Q(categories=self.product.category)),
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()

        if applicable_offer:
            discount = (base_price * applicable_offer.discount_percentage) / 100
            return base_price - discount
        return base_price


    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    

#address for user
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)

from django.db import models
from datetime import timedelta
from decimal import Decimal
from django.utils.timezone import now

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Return Pending', 'Return Pending'),
        ('Return Accepted', 'Return Accepted'),
        ('Paid', 'Paid'),  # Add 'Paid' status
    ]

    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
        ('wallet', 'Wallet'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='address')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    total_price = models.FloatField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    return_requested_at = models.DateTimeField(null=True, blank=True)
    offer_discount = models.FloatField(default=0)
    coupon_discount = models.FloatField(default=0)
    coupons = models.ManyToManyField(Coupon, related_name="used_orders", blank=True)
    subtotal = models.FloatField(default=0)
    discount_percentage = models.FloatField(default=0)
    payment_id = models.CharField(max_length=255, null=True, blank=True)  # Add Razorpay Payment ID

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    def reduce_inventory(self):
        for item in self.items.all():
            item.reduce_stock()

    @property
    def return_allowed(self):
        if self.status == 'Delivered':
            return now() <= self.created_at + timedelta(days=14)
        return False

    def refund_wallet(self):
        if self.payment_method == 'wallet' and self.status == 'Return Accepted':
            wallet = self.user.wallet
            if wallet:
                wallet.balance += Decimal(self.total_price)
                wallet.save()

    def restore_inventory(self):
        for item in self.items.all():
            if item.variant:
                item.variant.stock += item.quantity
                item.variant.save()
            elif item.product:
                item.product.stock += item.quantity
                item.product.save()

    @property
    def discounted_price(self):
        return self.total_price - self.offer_discount

    @property
    def offer_or_coupon(self):
        if self.coupon_discount > 0:
            return f"Coupon"
        elif self.offer_discount > 0:
            return f"Offer"
        return "None"

    @property
    def final_amount(self):
        discount_amount = (self.total_price * self.offer_discount / 100) + (self.total_price * self.coupon_discount / 100)
        return self.total_price - discount_amount

    def save(self, *args, **kwargs):
        """
        Mark the coupon as used when the order is placed.
        """
        # Save the Order instance first to ensure it gets an id
        super().save(*args, **kwargs)

        # Now that the Order has an id, we can update the ManyToMany relationship
        if self.coupons.exists():
            for coupon in self.coupons.all():
                coupon.used = True
                coupon.save()

    

#for use orderreturn
class OrderReturn(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='return_request')
    reason = models.TextField()
    additional_comments = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return Request for Order {self.order.id}"



# OrderItem Model(reduce the order count)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    def reduce_stock(self):
        
        if self.variant:
            self.variant.reduce_stock(self.quantity)
        elif self.product:
            self.product.reduce_stock(self.quantity)

    def __str__(self):
        if self.variant:
            return f"{self.variant.name} (x{self.quantity})"
        return f"{self.product.name} (x{self.quantity})"


#for user profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)  
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username


#user wishlist
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_on = models.DateField(default=now)
    created_at = models.DateTimeField( auto_now_add=True)
    

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product')
        ]

    def __str__(self):
        return f"{self.user.username}'s Wishlist - {self.product.name}"


#user wallet
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


#user transaction(store data for add and withdrow amount to wallet , not store product purchace using wallet)
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE,null=True, related_name='transactions')
    transaction_id = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
