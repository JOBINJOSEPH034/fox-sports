
from django.db import models
from admin_app.models import Product, ProductVariant,Coupon
from django.contrib.auth.models import User
from datetime import timedelta,datetime
from django.utils.timezone import now, make_aware
from django.utils.timezone import now
import random
from decimal import Decimal
import string

#for user cart 
class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    applied_coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 

     
    def update_total_price(self):
        """Method to recalculate the total price based on cart items"""
        total = sum(item.total_price for item in self.cartitem_set.all())
        self.total_price = total
        self.save()


    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        price = self.product.price + (self.variant.additional_price if self.variant else 0)
        return price * self.quantity

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


#order for user    
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
    ]

    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
        ('wallet', 'Wallet'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True,related_name='address') 
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)  
    product_name = models.CharField(max_length=100,null=True, blank=True)
    quantity = models.IntegerField(default=1)
    total_price = models.FloatField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES,default='cod')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    return_requested_at = models.DateTimeField(null=True, blank=True)
    offer_discount = models.FloatField(default=0)  # Add this field
    coupon_discount = models.FloatField(default=0)  # Add this field

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"
    
    def reduce_inventory(self):
        
        for item in self.items.all():
            item.reduce_stock()

    @property
    def return_allowed(self):
        if self.status == 'Delivered':
            # Directly compare with timezone-aware datetime
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

    def __str__(self):
        return self.user.username



class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_on = models.DateField(default=now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product')
        ]

    def __str__(self):
        return f"{self.user.username}'s Wishlist - {self.product.name}"

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

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