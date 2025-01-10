
from django import forms
from django.forms import modelformset_factory
from .models import Product, ProductVariant

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'brand', 'price', 'stock', 'image1', 'image2']

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'additional_price', 'stock']

# FormSet for ProductVariant
ProductVariantFormSet = modelformset_factory(
    ProductVariant,
    form=ProductVariantForm,
    extra=3,  # Render 3 empty forms initially for adding multiple variants
    can_delete=True,  # Allow deletion of existing variants
)
