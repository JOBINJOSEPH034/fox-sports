from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.

   
# model for category
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)


    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name=models.CharField(max_length=255)
    description=models.TextField(blank=True,null=True)

    def __str__(self):
        return self.name



class Product(models.Model):
    category = models.ForeignKey(
        'Category', 
        on_delete=models.CASCADE, 
        related_name='products'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)  # Total stock of the product
    brand = models.ForeignKey(
        'Brand', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='brand'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image1 = models.ImageField(
        upload_to='product_images/', 
        blank=True, 
        null=True
    )
    image2 = models.ImageField(
        upload_to='product_images/', 
        blank=True, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_variant = models.BooleanField(default=False)
    popularity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError("Insufficient stock!")
        

    def save(self, *args, **kwargs):
        # Sync product stock with variant stocks
        if self.is_variant:
            variants = self.variants.all()
            if len(variants) == 1:  # If there's only one variant, sync stocks
                variant = variants.first()
                self.stock = variant.stock
            else:
                total_variant_stock = sum(variant.stock for variant in variants)
                if total_variant_stock != self.stock:
                    raise ValidationError("The total stock of variants must match the product stock.")
        super().save(*args, **kwargs)

class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, 
        related_name="variants", 
        on_delete=models.CASCADE
    )
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    additional_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Use negative values for price reductions."
    )
    stock = models.PositiveIntegerField()  # Stock specific to this variant

    def __str__(self):
        # Use size and color to represent the variant
        return f"{self.product.name} - {self.size or ''} {self.color or ''}".strip()

    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError("Insufficient stock!")
    

    @property
    def total_price(self):
        # Calculate the total price for the variant (base product price + additional price)
        return self.product.price + self.additional_price