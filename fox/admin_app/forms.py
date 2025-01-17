from django import forms
from .models import Product, ProductVariant, Coupon

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'brand', 'stock', 'price','image1','image2']

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'additional_price', 'stock']


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_percentage', 'description', 'is_active']