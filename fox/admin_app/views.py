from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . models import Category,Product,Brand,ProductVariant
from user_app.models import Order
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import json
from .forms import ProductForm, ProductVariantForm
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.template.loader import render_to_string


# Create your views here.

#ADMIN HOME
@login_required
@never_cache
def admin_home(request):
  
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    deactivated_products = Product.objects.filter(is_active=False).count()

    total_categories = Category.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()
    deactivated_categories = Category.objects.filter(is_active=False).count()

    total_users = User.objects.filter(is_superuser=False).count()  # excluding admin users
    active_users = User.objects.filter(is_active=True).count()
    deactivated_users = User.objects.filter(is_active=False).count()

    context = {
        'total_products': total_products,
        'active_products': active_products,
        'deactivated_products': deactivated_products,
        'total_categories': total_categories,
        'active_categories': active_categories,
        'deactivated_categories': deactivated_categories,
        'total_users': total_users,
        'active_users': active_users,
        'deactivated_users': deactivated_users,
    }

    return render(request,'index.html',context)


#ADMIN PRODUCT
@login_required
@never_cache
def product_list(request):
    products = Product.objects.all()
    return render(request,'product.html', {'products': products})


def add_product(request):
    # Create a formset for the product variants (you can adjust extra to match the desired default empty forms)
    VariantFormSet = modelformset_factory(ProductVariant, form=ProductVariantForm, extra=4, can_delete=True)

    if request.method == "POST":
        # Handle the product form and the variant formset
        product_form = ProductForm(request.POST, request.FILES)  # Include files for image upload
        variant_formset = VariantFormSet(request.POST)

        if product_form.is_valid() and variant_formset.is_valid():
            # Save the product form
            product = product_form.save()

            # Save each variant form, associating it with the created product
            for variant_form in variant_formset:
                if variant_form.cleaned_data and not variant_form.cleaned_data.get('DELETE', False):
                    variant = variant_form.save(commit=False)
                    variant.product = product
                    variant.save()

            # Redirect to the product list or another page after saving
            return redirect('product')  # Adjust to the correct redirect URL

    else:
        # Initialize the form for GET request
        product_form = ProductForm()
        variant_formset = VariantFormSet(queryset=ProductVariant.objects.none())

    # Retrieve categories and brands for the dropdown
    categories = Category.objects.all()
    brands = Brand.objects.all()

    return render(request, 'add-product.html', {
        'product_form': product_form,
        'variant_formset': variant_formset,
        'categories': categories,
        'brands': brands,
    })
@login_required
@never_cache
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if we need to add an extra variant form
    extra_forms = int(request.GET.get('extra', 0))  # Default to 0
    VariantFormSet = modelformset_factory(ProductVariant, form=ProductVariantForm, extra=extra_forms, can_delete=True)

    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        variant_formset = VariantFormSet(request.POST, request.FILES, queryset=ProductVariant.objects.filter(product=product))

        if product_form.is_valid() and variant_formset.is_valid():
            product = product_form.save()

            # Save variants
            for form in variant_formset:
                if form.cleaned_data.get('DELETE'):
                    if form.instance.id:
                        form.instance.delete()
                else:
                    variant = form.save(commit=False)
                    variant.product = product
                    variant.save()

            messages.success(request, "Product updated successfully!")
            return redirect('product')
        else:
            messages.error(request, "There was an error updating the product.")
    else:
        product_form = ProductForm(instance=product)
        variant_formset = VariantFormSet(queryset=ProductVariant.objects.filter(product=product))

    categories = Category.objects.all()
    brands = Brand.objects.all()

    return render(request, 'edit-product.html', {
        'product_form': product_form,
        'variant_formset': variant_formset,
        'categories': categories,
        'brands': brands,
        'product': product,
        'extra_forms': extra_forms,  # Pass the extra_forms to template
    })



#for soft delete
def toggle_product_status(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = not product.is_active  
    product.save()
    status = "activated" if product.is_active else "soft deleted"
    messages.success(request, f"Product '{product.name}' has been {status}.")
    return redirect('product')


def permanent_delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()  
        messages.success(request, "Product permanently deleted.")
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
    
    return redirect('product') 


def product_variant_list(request, product_id):
    # Get the product object by product_id
    product = get_object_or_404(Product, id=product_id)
    # Get all variants related to this product
    variants = ProductVariant.objects.filter(product=product)
    
    # Prepare the response data
    variant_data = [{
        'size': variant.size,
        'color': variant.color,
        'stock': variant.stock,
        'total_price': variant.total_price
    } for variant in variants]

    return JsonResponse({'variants': variant_data})
#ADMIN CUSTOMER
@login_required
@never_cache
def customer_list(request):
    users = User.objects.filter(is_superuser=False)  # Non-admin users
    return render(request,'customer.html', {'users': users})



def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active=False
    user.save()
    messages.success(request, f"User {user.username} has been blocked.")
    return redirect('customer')

def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"User {user.username} has been unblocked.")
    return redirect('customer')


def edit_customer(request):
    return render(request,'edit-customer.html')




#ADMIN CATEGORIES
@login_required
@never_cache
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category.html', {'categories': categories})



def add_category(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        Category.objects.create(name=name, description=description)
        messages.success(request, "Category added successfully!")
        return redirect('category')
    return render(request, 'add-category.html')


def edit_category(request,category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == "POST":
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.save()
        messages.success(request, "Category updated successfully!")
        return redirect('category')
    return render(request, 'edit-category.html', {'category': category})


def toggle_category_status(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.is_active = not category.is_active                             
    category.save()
    status = "activated" if category.is_active else "soft deleted"
    messages.success(request, f"Category '{category.name}' has been {status}.")
    return redirect('category')



@login_required
@never_cache
def admin_order_management(request):
    orders = Order.objects.select_related('user', 'address').prefetch_related('items__product', 'items__variant').order_by('-created_at')
    return render(request, 'admin_order.html', {'orders': orders})


@login_required
def admin_update_order_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)
    order.status = status
    order.save()

    messages.success(request, f"Order {order.id} status updated to {status}.")
    return redirect('admin_order_management') 


@login_required
def admin_cancel_order(request, order_id):
   
    order = get_object_or_404(Order, id=order_id)

    if order.status in ['Pending', 'Processing', 'Shipped', 'Out for Delivery']:
        
        for item in order.items.all():
            if item.variant:
                item.variant.stock += item.quantity
                item.variant.save()
            elif item.product:
                item.product.stock += item.quantity
                item.product.save()

        # Update order status
        order.status = 'Cancelled'
        order.save()

        messages.success(request, f"Order {order.id} has been successfully canceled, and stock updated.")
    else:
        messages.error(request, f"Order {order.id} cannot be canceled at this stage.")

    return redirect('admin_order_management')


# for inventory management
@login_required
@never_cache
def inventory_management(request):
    products = Product.objects.all().prefetch_related('variants') 
   
    return render(request, 'inventory_management.html', {
        'products': products,
    
    })
# Update stock for products and variants
def update_stock(request, product_id, variant_id=None):
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id)
        if request.method == 'POST':
            new_stock = int(request.POST.get('stock', variant.stock))
            variant.stock = new_stock
            variant.save()
            # Sync the product stock if it's a single variant
            if variant.product.variants.count() == 1:  # If only one variant, sync the product stock
                variant.product.stock = new_stock
                variant.product.save()
            else:
                # Ensure product stock is the sum of all variant stocks
                total_variant_stock = sum(v.stock for v in variant.product.variants.all())
                variant.product.stock = total_variant_stock
                variant.product.save()
            messages.success(request, f"Stock updated for variant: {variant.size} - {variant.color}")
        return redirect('inventory_management')
    else:
        product = get_object_or_404(Product, id=product_id)
        if request.method == 'POST':
            new_stock = int(request.POST.get('stock', product.stock))
            product.stock = new_stock
            # Ensure the product stock is in sync with variant stock if there are variants
            if product.variants.exists():
                total_variant_stock = sum(variant.stock for variant in product.variants.all())
                if total_variant_stock != product.stock:
                    messages.error(request, "Total variant stock doesn't match product stock!")
                    return redirect('inventory_management')
            product.save()
            messages.success(request, f"Stock updated for product: {product.name}")
        return redirect('inventory_management')

def update_variant_stock(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    product = variant.product  # Get the associated product
    old_variant_stock = variant.stock  # Keep track of the old stock value

    if request.method == 'POST':
        new_stock = int(request.POST.get('stock', variant.stock))
        variant.stock = new_stock
        variant.save()

        # Adjust product stock based on variant stock changes
        if product.variants.count() > 1:
            # For multiple variants, ensure total variant stock matches product stock
            total_variant_stock = sum(v.stock for v in product.variants.all())
            product.stock = total_variant_stock
        else:
            # If only one variant, set product stock to match the variant stock
            product.stock = new_stock

        product.save()
        messages.success(request, f"Stock updated for variant: {variant.size} - {variant.color}")
    return redirect('inventory_management')


# Order Creation for Products
def create_order(request, product_id, variant_id=None):
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id)
        quantity = int(request.POST.get('quantity', 1))

        if variant.stock >= quantity:
            variant.stock -= quantity
            variant.save()

            # Reduce the product stock as well
            variant.product.stock -= quantity
            variant.product.save()

            Order.objects.create(
                user=request.user, 
                product=variant.product,  
                variant=variant,  
                quantity=quantity,
                total_price=variant.product.price * quantity  
            )
            messages.success(request, f"Order placed for variant: {variant.size} - {variant.color}")
        else:
            messages.error(request, f"Insufficient stock for variant: {variant.size} - {variant.color}")
        return redirect('product_detail', variant.product.id)
    else:
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        if product.stock >= quantity:
            product.stock -= quantity
            product.save()

            Order.objects.create(
                user=request.user, 
                product=product,  
                quantity=quantity,
                total_price=product.price * quantity  
            )
            messages.success(request, f"Order placed for product: {product.name}")
        else:
            messages.error(request, f"Insufficient stock for product: {product.name}")
        return redirect('product_detail', product.id)


def create_order_with_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    quantity = int(request.POST.get('quantity', 1))

    if variant.stock >= quantity:
        variant.stock -= quantity
        variant.save()

        # Reduce the product stock as well
        product = variant.product
        product.stock -= quantity
        product.save()

        Order.objects.create(
            user=request.user, 
            product=variant.product, 
            variant=variant,  
            quantity=quantity,
            total_price=variant.product.price * quantity
        )

        messages.success(request, f"Order placed successfully for {variant.product.name} ({variant.size} - {variant.color})!")
    else:
        messages.error(request, f"Insufficient stock for {variant.product.name} ({variant.size} - {variant.color}).")

    return redirect('product_detail', variant.product.id)
