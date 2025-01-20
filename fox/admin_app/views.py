from time import timezone
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . models import Category,Product,Brand,ProductVariant,Coupon,Offer
from user_app.models import Order,OrderItem
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import ProductForm, ProductVariantForm, CouponForm 
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime

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
    products = Product.objects.all().order_by('-created_at')

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




# Display all coupons
def coupon_list(request):
    coupons = Coupon.objects.all()
    if request.method == 'POST':
        code = request.POST.get('code')
        discount_percentage = request.POST.get('discount_percentage')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'

        # Add coupon to the database
        Coupon.objects.create(code=code, discount_percentage=discount_percentage, description=description, is_active=is_active)
        messages.success(request, 'Coupon created successfully!')

    return render(request, 'coupon_management.html', {'coupons': coupons})

# Delete a coupon
def delete_coupon(request, coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    coupon.delete()
    messages.success(request, 'Coupon deleted successfully!')
    return redirect('coupon_list')

def manage_offers(request):
    offers = Offer.objects.all()  # Fetch all offers
    products = Product.objects.all()  # Fetch all products
    categories = Category.objects.all()  # Fetch all categories

    
    # Pagination
    paginator = Paginator(offers, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Add the related products, categories, or referral codes for each offer
    offers_with_details = []
    for offer in offers:
        applied_items = []
        if offer.offer_type == 'product':
            applied_items = [product.name for product in offer.products.all()]
        elif offer.offer_type == 'category':
            applied_items = [category.name for category in offer.categories.all()]
        elif offer.offer_type == 'referral':
            applied_items = [f"Referral Code: {offer.referral_code}"]
        
        offers_with_details.append({
            'offer': offer,
            'applied_items': applied_items
        })

    if request.method == 'POST':
        offer_id = request.POST.get('offer_id', None)  # Use `None` if not editing an offer
        name = request.POST.get('name')
        discount_percentage = request.POST.get('discount_percentage')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        offer_type = request.POST.get('offer_type')
        products_selected = request.POST.getlist('products')
        categories_selected = request.POST.getlist('categories')
        referral_code = request.POST.get('referral_code', '')

        # Ensure all required fields are provided
        if not name or not discount_percentage or not start_date or not end_date or not offer_type:
            messages.error(request, "All fields are required.")
            return redirect('manage_offers')

        if offer_id:  # Edit existing offer
            try:
                offer = Offer.objects.get(id=offer_id)
                offer.name = name
                offer.discount_percentage = discount_percentage
                offer.start_date = start_date
                offer.end_date = end_date
                offer.offer_type = offer_type

                # Update related fields based on offer type
                if offer_type == 'product':
                    offer.products.set(Product.objects.filter(id__in=products_selected))
                    offer.categories.clear()
                    offer.referral_code = ''
                elif offer_type == 'category':
                    offer.categories.set(Category.objects.filter(id__in=categories_selected))
                    offer.products.clear()
                    offer.referral_code = ''
                elif offer_type == 'referral':
                    offer.referral_code = referral_code
                    offer.products.clear()
                    offer.categories.clear()

                offer.save()
                messages.success(request, "Offer updated successfully!")
            except Offer.DoesNotExist:
                messages.error(request, "Offer not found.")
        else:  # Create new offer
            offer = Offer.objects.create(
                name=name,
                discount_percentage=discount_percentage,
                start_date=start_date,
                end_date=end_date,
                offer_type=offer_type
            )
            if offer_type == 'product':
                offer.products.set(Product.objects.filter(id__in=products_selected))
            elif offer_type == 'category':
                offer.categories.set(Category.objects.filter(id__in=categories_selected))
            elif offer_type == 'referral':
                offer.referral_code = referral_code
            offer.save()
            messages.success(request, "Offer created successfully!")

        return redirect('manage_offers')

    return render(request, 'offer_management.html', {
        'offers_with_products': offers_with_details,
        'products': products,
        'categories': categories,
         'page_obj': page_obj,
    })


def delete_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    offer.delete()
    messages.success(request, "Offer deleted successfully!")
    return redirect('manage_offers')




from django.shortcuts import render
from django.db.models import Sum, F, Count

def dashboard_view(request):
    # Aggregating total sales
    total_sales = Order.objects.filter(status='Delivered').aggregate(total_sales=Sum('total_price'))['total_sales'] or 0
    
    # Aggregating total orders
    total_orders = Order.objects.count()
    
    # Aggregating number of delivered orders
    delivered_orders = Order.objects.filter(status='Delivered').count()
    
    # Aggregating number of cancelled orders
    cancelled_orders = Order.objects.filter(status='Cancelled').count()
    
    # Aggregating total discount applied through offers or coupons
    total_discount = 0
    offers = Offer.objects.filter(end_date__gte=timezone.now())  # Offers still valid
    coupons = Coupon.objects.filter(is_active=True)  # Active coupons
    for offer in offers:
        total_discount += offer.discount_percentage
    for coupon in coupons:
        total_discount += coupon.discount_percentage
    
    # Product statistics (Active/Deactivated products)
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    deactivated_products = Product.objects.filter(is_active=False).count()

    # Category statistics (Active/Deactivated categories)
    total_categories = Category.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()
    deactivated_categories = Category.objects.filter(is_active=False).count()

    # User statistics (Active/Deactivated users)
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    deactivated_users = User.objects.filter(is_active=False).count()

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'total_discount': total_discount,
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

    return render(request, 'index.html', context)






# admin_app/views.py

from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import openpyxl
from user_app.models import Order, OrderItem  # Import Order and OrderItem from user_app
import io

from django.db.models import F, Sum
from datetime import datetime, timedelta
from django.utils import timezone

from django.core.paginator import Paginator

@login_required
def sales_report(request):
    # Default filters
    date_filter = request.GET.get('date_filter', 'today')  # Default to today
    
    # Date range filters (same as before)
    if date_filter == 'today':
        start_date = timezone.make_aware(datetime.combine(datetime.today(), datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(datetime.today(), datetime.max.time()))
    elif date_filter == 'this_week':
        today = datetime.today()
        start_date = timezone.make_aware(datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(today + timedelta(days=(6 - today.weekday())), datetime.max.time()))
    elif date_filter == 'this_month':
        today = datetime.today()
        start_date = timezone.make_aware(datetime.combine(today.replace(day=1), datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(today.replace(day=1) + timedelta(days=32), datetime.min.time()) - timedelta(seconds=1))
    else:  # custom date range
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')
        if start_date_str and end_date_str:
            start_date = timezone.make_aware(datetime.combine(datetime.strptime(start_date_str, '%Y-%m-%d'), datetime.min.time()))
            end_date = timezone.make_aware(datetime.combine(datetime.strptime(end_date_str, '%Y-%m-%d'), datetime.max.time()))
        else:
            start_date = end_date = None

    # Filter Orders based on the selected date range
    orders = Order.objects.all().order_by('-created_at')
    if start_date and end_date:
        orders = orders.filter(created_at__range=[start_date, end_date])

    # Pagination: Show 10 orders per page
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Filter out canceled orders from the summary calculations
    non_canceled_orders = orders.exclude(status='canceled')

    # Price range filters (same as before)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        non_canceled_orders = non_canceled_orders.filter(total_price__gte=float(min_price))
    if max_price:
        non_canceled_orders = non_canceled_orders.filter(total_price__lte=float(max_price))

    # Aggregation for summary statistics (excluding canceled orders)
    total_sales = non_canceled_orders.aggregate(total_sales=Sum('total_price'))['total_sales'] or 0
    total_orders = non_canceled_orders.count()
    
    # Calculate total discounts (excluding canceled orders)
    total_discount = non_canceled_orders.aggregate(
        total_discount=Sum(F('offer_discount') + F('coupon_discount'))
    )['total_discount'] or 0

    average_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    context = {
        'orders': page_obj,  # Paginated orders
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_discount': total_discount,
        'average_order_value': round(average_order_value, 2),
        'date_filter': date_filter,
    }

    return render(request, 'sales_report.html', context)


def export_to_excel(request):
    # Fetch orders from the database
    orders = Order.objects.all()
    
    # Create Excel Workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Sales Report'
    
    # Add header row
    ws.append(['Order ID', 'Date', 'Customer', 'Items', 'Subtotal', 'Offer Discount', 'Final Amount', 'Status'])
    
    # Add order data
    for order in orders:
        # Join product names or IDs into a single string
        items = ', '.join([str(item.product_id) for item in order.items.all()])  # Convert to string
        
        # Write the order data into the Excel sheet
        ws.append([
            order.id, 
            order.created_at.strftime('%Y-%m-%d'),
            order.user.username,
            items,
            order.total_price,
            order.offer_discount,
            order.total_price - order.offer_discount,
            order.status
        ])
    
    # Save the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'
    wb.save(response)
    
    return response


def export_to_pdf(request):
    orders = Order.objects.all()
    html_content = render_to_string('sales_report.html', {'orders': orders, 'is_pdf': True})
    pdf_file = HTML(string=html_content).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=sales_report.pdf'
    return response
