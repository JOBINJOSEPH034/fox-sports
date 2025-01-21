from django.db import models
from django.db import transaction
from datetime import date


   
# model for category
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Discount for the entire category

    def get_offer_discount(self):
        if self.offer and self.offer.is_valid():
            return self.offer.discount_percentage
        return 0


    def __str__(self):
        return self.name
    

#model for brand    
class Brand(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField(blank=True,null=True)
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return self.name

#model for product
class Product(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)  
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, null=True, blank=True, related_name='brand')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image1 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_variant = models.BooleanField(default=False)
    popularity = models.PositiveIntegerField(default=0)
    product_offers = models.ManyToManyField('Offer', related_name='offered_products', blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0) 
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  

    def __str__(self):
        return self.name

    def reduce_stock(self, quantity):                      #Reduces stock when an order is placed
       
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError("Insufficient stock!")
        
    def save(self, *args, **kwargs):  
        max_discount = max(self.discount_percentage, self.category.discount_percentage)
                                                                                 
        if max_discount > 0:                                                             # Apply discount price if any discount exists
            self.discount_price = self.price - (self.price * max_discount / 100)
        else:
            self.discount_price = None                                                    # No discount applied

        if self.discount_percentage == 0.0 and self.discount_price is not None:
            if self.price > self.discount_price:
                self.discount_percentage = (1 - (self.discount_price / self.price)) * 100
            else:
                self.discount_percentage = 0.0
                                                   
        if self.discount_price:                                                # Recalculate the total price considering both the discount and product price
            self.total_price = self.discount_price
        else:
            self.total_price = self.price

        super().save(*args, **kwargs)

def get_discounted_price(self):
    if self.offer and self.offer.is_valid():
        return self.price * (1 - self.offer.discount_percentage / 100)
    return self.price

#model for product varient
class ProductVariant(models.Model):
    product = models.ForeignKey(Product,related_name="variants", on_delete=models.CASCADE)
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2,help_text="Use negative values for price reductions.")
    stock = models.PositiveIntegerField() 
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    
    def __str__(self):
        product_name = getattr(self.product, 'name', 'Unnamed Product')
        return f"{product_name} - {self.size or ''} {self.color or ''}".strip()


    def save(self, *args, **kwargs):
        
        base_price = self.product.price + self.additional_price
        max_discount = max(self.product.discount_percentage, self.product.category.discount_percentage)
        if max_discount > 0:
            self.discount_price = base_price - (base_price * max_discount / 100)
        else:
            self.discount_price = None  

        super().save(*args, **kwargs)


    def reduce_stock(self, quantity):
        with transaction.atomic():  
            if self.stock >= quantity:
                self.stock -= quantity
                self.save()  
            else:
                raise ValueError("Insufficient stock!")

    
    @property
    def total_price(self):
        price_with_discount = self.product.price + self.additional_price
        max_discount = max(self.product.discount_percentage, self.product.category.discount_percentage)
        if max_discount > 0:
            return price_with_discount - (price_with_discount * max_discount / 100)
        return price_with_discount

#model for coupon
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Offer(models.Model):
    PRODUCT = 'product'
    CATEGORY = 'category'
    REFERRAL = 'referral'

    OFFER_TYPES = [
        (PRODUCT, 'Product Offer'),
        (CATEGORY, 'Category Offer'),
        (REFERRAL, 'Referral Offer'),
    ]

    name = models.CharField(max_length=255)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES)
    products = models.ManyToManyField(Product, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    referral_code = models.CharField(max_length=255, blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.discount_percentage}%"
    
    def is_valid(self):        #        Check if the offer is valid based on the current date
        return self.start_date <= date.today() <= self.end_date
    
    def apply_discount_to_product(self):                            # Apply discount to products linked with this offer

        if self.offer_type == self.PRODUCT:
            for product in self.products.all():
                self._apply_discount_to_product_and_variants(product)
        elif self.offer_type == self.CATEGORY:
            for category in self.categories.all():
                products_in_category = Product.objects.filter(category=category)
                for product in products_in_category:
                    self._apply_discount_to_product_and_variants(product)

    def _apply_discount_to_product_and_variants(self, product):
        original_price = product.price
        discount_amount = (original_price * self.discount_percentage) / 100
        discounted_price = original_price - discount_amount

        product.discount_price = discounted_price
        product.save()

        for variant in product.variants.all():
            variant_base_price = variant.product.price + variant.additional_price
            variant_discounted_price = variant_base_price - (variant_base_price * self.discount_percentage) / 100
            variant.discount_price = variant_discounted_price
            variant.save()


#model for sales report
class SalesReport(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    total_orders = models.PositiveIntegerField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)
    total_refunds = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sales Report: {self.start_date} to {self.end_date}"
