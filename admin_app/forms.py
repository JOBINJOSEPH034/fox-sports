from django import forms
from .models import Product, ProductVariant, Coupon

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'brand', 'stock', 'price','image1','image2']

    def __init__(self, *args, **kwargs):                             # for img show in the edit product page
        super(ProductForm, self).__init__(*args, **kwargs)
        if self.instance.pk:                                                
        
            if self.instance.image1:
                self.fields['image1'].widget.attrs.update({'data-preview': self.instance.image1.url})
            if self.instance.image2:
                self.fields['image2'].widget.attrs.update({'data-preview': self.instance.image2.url})

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'additional_price', 'stock']


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_percentage', 'description', 'is_active']