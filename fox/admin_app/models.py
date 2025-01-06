from django.db import models

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



# model for product
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    brand=models.ForeignKey(Brand, on_delete=models.CASCADE,null=True,blank=True,related_name='brand')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image1 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=True)
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


   #for product varient (not working) 
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name="variants", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price_difference = models.DecimalField(max_digits=10, decimal_places=2, help_text="Use negative values for price reductions.")
    stock = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    def reduce_stock(self, quantity):
        
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError("Insufficient stock!")




