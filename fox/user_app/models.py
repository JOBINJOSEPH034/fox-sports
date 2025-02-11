
from django.db import models
from admin_app.models import Product, ProductVariant,Coupon,Offer,transaction
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Q
from decimal import Decimal
from django.utils import timezone
import uuid





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
    

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        base_price = self.product.price + (self.variant.additional_price if self.variant else 0)
        discounted_price = self.get_discounted_price()
        return discounted_price * self.quantity

    def get_discounted_price(self):
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
        ('Paid', 'Paid'),
        ('Payment Failed', 'Failed'),  
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
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    return_requested_at = models.DateTimeField(null=True, blank=True)
    offer_discount = models.FloatField(default=0)
    coupon_discount = models.FloatField(default=0)
    coupons = models.ManyToManyField(Coupon, related_name="used_orders", blank=True)
    subtotal = models.FloatField(default=0)
    discount_percentage = models.FloatField(default=0)
    payment_id = models.CharField(max_length=255, null=True, blank=True)  
    is_refunded = models.BooleanField(default=False)  
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_attempts = models.IntegerField(default=0)
    payment_failed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    

    def reduce_inventory(self):
        try:
            with transaction.atomic():
                for item in self.items.select_related('variant', 'product').all():
                    if item.variant:
                        if item.variant.stock < item.quantity:
                            raise ValueError(f"Insufficient stock for variant {item.variant.id}. Required: {item.quantity}, Available: {item.variant.stock}")
                        
                        item.variant.stock -= item.quantity
                        item.variant.save(update_fields=['stock'])
                    
                    elif item.product:
                        if item.product.stock < item.quantity:
                            raise ValueError(f"Insufficient stock for product {item.product.id}. Required: {item.quantity}, Available: {item.product.stock}")
                        
                        item.product.stock -= item.quantity
                        item.product.save(update_fields=['stock'])
        except Exception as e:
            raise


    def restore_inventory(self):
        try:
            with transaction.atomic():
                for item in self.items.select_related('variant', 'product').all():
                    if item.status in ['Cancelled', 'Return Accepted'] and not item.is_refunded:
                        if item.variant:
                            item.variant.stock += item.quantity
                            item.variant.save(update_fields=['stock'])
                        elif item.product:
                            item.product.stock += item.quantity
                            item.product.save(update_fields=['stock'])

                        item.is_refunded = True
                        item.save(update_fields=['is_refunded'])
        except Exception as e:
            raise


    def refund_wallet(self):

        try:
            with transaction.atomic():
                wallet, created = Wallet.objects.get_or_create(user=self.user)
                total_refund_amount = Decimal('0')

                for item in self.items.all():  
                    if item.status in ['Cancelled', 'Return Accepted'] and not item.is_refunded:
                        refund_amount = Decimal(str(item.total_price))  
                    
                        wallet.balance += refund_amount
                        total_refund_amount += refund_amount
                        wallet.save()

                        item.is_refunded = True
                        item.save(update_fields=['is_refunded'])

                        Transaction.objects.create(
                            wallet=wallet,
                            transaction_id=f"RF{str(uuid.uuid4())[:8].upper()}",
                            type='deposit',
                            amount=refund_amount,
                            description=f"Refund for {item.product_name} (Order #{self.id})"
                    )
        except Exception as e:
            return False


    @property
    def has_returns(self):
        return self.items.filter(orderreturn__isnull=False).exists()

    @property
    def all_items_returned(self):
        return all(item.orderreturn is not None for item in self.items.all())

    @property
    def return_allowed(self):
        if not self.delivered_at:
            return False
    
        return_period_days = 7
        current_time = now()
        return_deadline = self.delivered_at + timedelta(days=return_period_days)
    
        is_allowed = (self.status == 'Delivered' and 
                     self.delivered_at is not None and 
                     current_time <= return_deadline)
    
   
    
        return is_allowed

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

    def is_retry_period_expired(self):
        if self.payment_failed_at:
            return (timezone.now() - self.payment_failed_at).days > 7
        return False

    def can_retry_payment(self):
        return self.status == 'failed' and self.payment_attempts < 2 and not self.is_retry_period_expired()

    def save(self, *args, **kwargs):
        original_status = None
        if self.pk:
            try:
                original_order = Order.objects.get(pk=self.pk)
                original_status = original_order.status
            except Order.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if original_status != self.status:
            
            if self.status == 'Pending' and original_status != 'Pending':
                try:
                    self.reduce_inventory()
                except Exception as e:
                    self.status = 'Payment Failed'
                    self.save(update_fields=['status'])
                    raise
            
            elif self.status in ['Cancelled', 'Return Accepted'] and not self.is_refunded:
                try:
                    self.restore_inventory()
                    self.refund_wallet()
                except Exception as e:
                    raise

            self.items.all().update(status=self.status)    




# OrderItem Model(reduce the order count)
class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Return Pending', 'Return Pending'),
        ('Return Accepted', 'Return Accepted'),
        ('Paid', 'Paid'),
        ('Payment Failed', 'Failed'),
    ]
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    returned_quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    is_refunded = models.BooleanField(default=False)

    
    def save(self, *args, **kwargs):
        if self.order and self.status != self.order.status:
            self.status = self.order.status

        if not self.pk:  
            self.reduce_stock()

        super().save(*args, **kwargs)

    def reduce_stock(self):
        with transaction.atomic():
            if self.variant:
                self.variant.reduce_stock(self.quantity)
            elif self.product:
                self.product.reduce_stock(self.quantity)

    def restore_stock(self):
        with transaction.atomic():
            if self.variant:
                self.variant.increase_stock(self.quantity)
            elif self.product:
                self.product.increase_stock(self.quantity)

    def update_status(self, new_status):
        if new_status in ['Cancelled', 'Return Accepted'] and self.status not in ['Cancelled', 'Return Accepted']:
            self.restore_stock()
        self.status = new_status
        self.save()
    
   

#for use orderreturn
class OrderReturn(models.Model):

    RETURN_STATUS_CHOICES = (
        ('Return Pending', 'Return Pending'),
        ('Return Accepted', 'Return Accepted'),
        ('Return Rejected', 'Return Rejected'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    additional_comments = models.TextField(blank=True, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='orderreturn',blank=True, null=True)
    image = models.ImageField(upload_to='return_proofs/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default='Return Pending')
    return_requested_at = models.DateTimeField(default=now) 
    return_quantity = models.PositiveIntegerField(default=1)
    processed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk: 
            self.order = self.order_item.order
        super().save(*args, **kwargs)

    def process_return(self):
        if not self.processed and self.status == 'Return Accepted':
            try:
                with transaction.atomic():
                    if self.return_quantity > (self.order_item.quantity - self.order_item.returned_quantity):
                        raise ValueError("Return quantity exceeds available quantity")

                    if self.order_item.variant:
                        self.order_item.variant.increase_stock(self.return_quantity)
                    elif self.order_item.product:
                        self.order_item.product.increase_stock(self.return_quantity)

                    self.order_item.returned_quantity += self.return_quantity
                    self.order_item.status = 'Return Accepted'
                    self.order_item.save()

                    if not self.order.is_refunded:
                        self.order.refund_wallet()

                    self.processed = True
                    self.save()
                    return True
            except Exception as e:
                raise
        return False


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

    def __str__(self):
        return f"Wallet of {self.user.username}"

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
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} ({self.type}) - {self.amount}"
 