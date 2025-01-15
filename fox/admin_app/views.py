from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . models import Category,Product,Brand,ProductVariant
from user_app.models import Order
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import ProductForm, ProductVariantForm
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.core.paginator import Paginator

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

    paginator = Paginator(products, 8)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'product.html',{'page_obj': page_obj})


@login_required
@never_cache
def add_product(request):
    VariantFormSet = modelformset_factory(ProductVariant, form=ProductVariantForm, extra=4, can_delete=True) # extra 4 is varient nos that can increase if want more varient 
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES)  
        variant_formset = VariantFormSet(request.POST)

        if product_form.is_valid() and variant_formset.is_valid():
            product = product_form.save()

            for variant_form in variant_formset:
                if variant_form.cleaned_data and not variant_form.cleaned_data.get('DELETE', False):
                    variant = variant_form.save(commit=False)
                    variant.product = product
                    variant.save()

            return redirect('product')  

    else:
        product_form = ProductForm()
        variant_formset = VariantFormSet(queryset=ProductVariant.objects.none())

    categories = Category.objects.all()
    brands = Brand.objects.filter(is_active=True)

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
    extra_forms = int(request.GET.get('extra', 0))  # Default to 0
    VariantFormSet = modelformset_factory(ProductVariant, form=ProductVariantForm, extra=extra_forms, can_delete=True)

    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        variant_formset = VariantFormSet(request.POST, request.FILES, queryset=ProductVariant.objects.filter(product=product))

        if product_form.is_valid() and variant_formset.is_valid():
            product = product_form.save()

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
        'extra_forms': extra_forms, 
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

# product list view button 
def product_variant_list(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = ProductVariant.objects.filter(product=product)

    variant_data = [{
        'size': variant.size,
        'color': variant.color,
        'stock': variant.stock,
        'total_price': variant.total_price
    } for variant in variants]

    return JsonResponse({'variants': variant_data})


#ADMIN CUSTOMER
def customer_list(request):
    users = User.objects.filter(is_superuser=False)  # Non-admin users
    
    # Paginate the users
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')  # Get the page number from the request
    page_obj = paginator.get_page(page_number)  # Get the page object

    return render(request, 'customer.html', {'page_obj': page_obj})



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
    categories = Category.objects.all()  # Fetch all categories
    
    # Paginate the categories
    paginator = Paginator(categories, 10)  # Show 10 categories per page
    page_number = request.GET.get('page')  # Get the page number from the request
    page_obj = paginator.get_page(page_number)  # Get the page object
    
    return render(request, 'category.html', {'page_obj': page_obj})


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


from django.core.paginator import Paginator

@login_required
@never_cache
def admin_order_management(request):
    orders = Order.objects.select_related('user', 'address') \
        .prefetch_related('items__product', 'items__variant') \
        .order_by('-created_at')

    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)

    return render(request, 'admin_order.html', {'orders': orders_page})
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





# For admin inventory management with pagination
@login_required
@never_cache
def inventory_management(request):
    # Retrieve all products and prefetch their variants to avoid extra queries
    products = Product.objects.all().prefetch_related('variants')

    # Pagination logic: Display 10 products per page
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventory_management.html', {
        'page_obj': page_obj,  # Paginated products
    })

# Update stock for all variants of a product
@login_required
def update_stock_for_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        new_stock = int(request.POST.get('stock', product.stock))  # Get new stock value for the product
        if new_stock != product.stock:  # Only update if the stock value has changed
            product.stock = new_stock
            product.save()

            # Update the stock of all variants for this product
            for variant in product.variants.all():
                variant.stock = new_stock
                variant.save()

            messages.success(request, f"Stock updated for product: {product.name} and all its variants.")
        return redirect('inventory_management')

    return redirect('inventory_management')

# AJAX-based stock update for all variants of a product
@login_required
def update_variant_stock(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    product = variant.product

    if request.method == 'POST':
        new_stock = int(request.POST.get('stock', variant.stock))  # Get new stock value for the variant
        if new_stock != variant.stock:  # Only update if the stock value has changed
            variant.stock = new_stock
            variant.save()

            # Update the product stock as the sum of all variants' stock
            total_variant_stock = sum(v.stock for v in product.variants.all())
            product.stock = total_variant_stock
            product.save()

            messages.success(request, f"Stock updated for variant: {variant.size} - {variant.color}")
        return redirect('inventory_management')

    return redirect('inventory_management')
  

def create_order(request, product_id, variant_id=None):
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id)
        quantity = int(request.POST.get('quantity', 1))

        if variant.stock >= quantity:
            variant.stock -= quantity
            variant.save()

            variant.product.stock -= quantity  # Reduce the product stock as well
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

        product = variant.product          # Reduce the product stock as well
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


def brand_management(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        if name:
            Brand.objects.create(name=name, description=description)
            messages.success(request, "Brand added successfully!")
            return redirect("brand_management")
        else:
            messages.error(request, "Brand name is required.")

    # Pagination logic
    brands = Brand.objects.all()
    paginator = Paginator(brands, 10)  # Show 10 brands per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    brand_data = []
    for brand in page_obj:
        products = Product.objects.filter(brand=brand)
        total_stock = sum(product.stock for product in products)
        brand_data.append({
            "brand": brand,
            "product_count": products.count(),
            "total_stock": total_stock,
        })

    context = {
        "brand_data": brand_data,
        "page_obj": page_obj,  # Pass the page object to the template
    }

    return render(request, "brand_management.html", context)


# Deactivate Brand
def deactivate_brand(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    brand.is_active = False  
    brand.save()
    messages.success(request, f"Brand {brand.name} has been deactivated.")
    return redirect("brand_management")

# Delete Brand
def delete_brand(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    brand.delete()
    messages.success(request, f"Brand {brand.name} has been deleted.")
    return redirect("brand_management")


def toggle_brand_status(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    
    brand.is_active = not brand.is_active  #
    brand.save()

    status = "deactivated" if not brand.is_active else "activated"
    messages.success(request, f"Brand {brand.name} has been {status}.")
    
    return redirect("brand_management")
