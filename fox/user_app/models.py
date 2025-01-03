
from django.db import models

from admin_app.models import Product, ProductVariant
from django.contrib.auth.models import User
from django.utils.timezone import now

class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

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
        # Calculate the total price considering the variant if available
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
        # If this address is marked as default, unmark other addresses as default
        if self.is_default:
            # Unset all other addresses for the user as default
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
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True) 
    product_name = models.CharField(max_length=100,null=True, blank=True)
    quantity = models.IntegerField(default=1)
    total_price = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)


   

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"




class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)  # Optional default address

    def __str__(self):
        return self.user.username

