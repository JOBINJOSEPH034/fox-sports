from time import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from . models import Category,Product,Brand,ProductVariant,Coupon,Offer
from user_app.models import Order,OrderItem
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import ProductForm, ProductVariantForm
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime,timedelta
from django.db.models import Sum, F
from django.utils import timezone
import openpyxl  
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from django.db.models.functions import TruncMonth,TruncYear


from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncYear, TruncWeek, TruncDay
from django.http import JsonResponse



from django.db.models import Sum, F
from django.http import JsonResponse
from user_app.models import OrderItem
from django.db.models.functions import ExtractWeek, ExtractYear, ExtractMonth, ExtractDay
from django.db.models import Sum, F
from django.http import JsonResponse


from django.shortcuts import render
from django.db.models import Sum
# Create your views here.

@login_required
@never_cache

def admin_home(request):
    print('Admin home view executed')  # Debugging print statement

    # Top-selling products, categories, and brands
    top_products = OrderItem.objects.values('product__name') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')[:10]

    top_categories = OrderItem.objects.values('product__category__name') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')[:10]

    top_brands = OrderItem.objects.values('product__brand__name') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')[:10]

    # Sales data based on filter type
    filter_type = request.GET.get('filter', 'daily')

    if filter_type == 'monthly':
        sales = (
            OrderItem.objects
            .annotate(month=ExtractMonth('order__created_at'), year=ExtractYear('order__created_at'))
            .values('month', 'year')
            .annotate(total_sales=Sum('quantity'))
            .order_by('year', 'month')
        )
        labels = [f"{sale['month']}-{sale['year']}" for sale in sales]

    elif filter_type == 'yearly':
        sales = (
            OrderItem.objects
            .annotate(year=ExtractYear('order__created_at'))
            .values('year')
            .annotate(total_sales=Sum('quantity'))
            .order_by('year')
        )
        labels = [str(sale['year']) for sale in sales]

    elif filter_type == 'weekly':
        sales = (
            OrderItem.objects
            .annotate(week=ExtractWeek('order__created_at'), year=ExtractYear('order__created_at'))
            .values('week', 'year')
            .annotate(total_sales=Sum('quantity'))
            .order_by('year', 'week')
        )
        labels = [f"Week {sale['week']}-{sale['year']}" for sale in sales]

    elif filter_type == 'daily':
        sales = (
            OrderItem.objects
            .annotate(day=ExtractDay('order__created_at'), month=ExtractMonth('order__created_at'), year=ExtractYear('order__created_at'))
            .values('day', 'month', 'year')
            .annotate(total_sales=Sum('quantity'))
            .order_by('year', 'month', 'day')
        )
        labels = [f"{sale['day']}-{sale['month']}-{sale['year']}" for sale in sales]

    else:
        return JsonResponse({'error': 'Invalid filter type'}, status=400)

    data = [sale['total_sales'] for sale in sales]

    

    context = {
        'top_products': top_products,
        'top_categories': top_categories,
        'top_brands': top_brands,
        'sales_labels': labels,
        'sales_data': data,
    }

    return render(request, 'index.html', context)


@login_required
@never_cache
def product_list(request):
    query = request.GET.get('q', '').strip() 
    products = Product.objects.all().order_by('-created_at')

    
    if query:
        products = products.filter(name__icontains=query)  

    paginator = Paginator(products, 8)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'product.html', {'page_obj': page_obj, 'query': query})


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
    extra_forms = int(request.GET.get('extra', 0)) 
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
    query = request.GET.get('q', '').strip()  
    users = User.objects.filter(is_superuser=False)

    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query)

    paginator = Paginator(users,5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'customer.html', {'page_obj': page_obj, 'query': query})


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


def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('customer')


def edit_customer(request):
    return render(request,'edit-customer.html')




#ADMIN CATEGORIES
@login_required
@never_cache
def category_list(request):
    query = request.GET.get('q', '')  
    categories = Category.objects.all()

    if query:
        categories = categories.filter(name__icontains=query)  

    paginator = Paginator(categories, 10)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)  

    return render(request, 'category.html', {'page_obj': page_obj, 'query': query})


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
    orders = Order.objects.select_related('user', 'address') \
        .prefetch_related('items__product', 'items__variant') \
        .order_by('-created_at')

    search_query = request.GET.get('search', '').strip()
    
    if search_query:
        orders = orders.filter(
            Q(user__username__icontains=search_query) |  
            Q(items__product__name__icontains=search_query) |  
            Q(status__icontains=search_query)  
        ).distinct()

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)

    return render(request, 'admin_order.html', {'orders': orders_page, 'search_query': search_query})

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

        order.status = 'Cancelled'
        order.save()

        messages.success(request, f"Order {order.id} has been successfully canceled, and stock updated.")
    else:
        messages.error(request, f"Order {order.id} cannot be canceled at this stage.")

    return redirect('admin_order_management')





# For admin inventory management 
@login_required
@never_cache
def inventory_management(request):
    search_query = request.GET.get('search', '').strip()
    
    products = Product.objects.all().prefetch_related('variants')
    
    if search_query:
        products = products.filter(name__icontains=search_query)  
    
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventory_management.html', {
        'page_obj': page_obj,
        'search_query': search_query,  
    })


@login_required
def update_stock_for_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        new_stock = int(request.POST.get('stock', product.stock))   
        if new_stock != product.stock:                             
            product.stock = new_stock
            product.save()

            for variant in product.variants.all():
                variant.stock = new_stock
                variant.save()

            messages.success(request, f"Stock updated for product: {product.name} and all its variants.")
        return redirect('inventory_management')

    return redirect('inventory_management')




@login_required
def update_variant_stock(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)

    if request.method == 'POST':
        try:
            new_stock = int(request.POST.get('stock'))
            
            if new_stock != variant.stock:
                variant.stock = new_stock
                variant.save()

                product = variant.product
                product.stock = sum(v.stock for v in product.variants.all())
                product.save()

            return JsonResponse({'success': True})
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid stock value'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def create_order(request, product_id, variant_id=None):
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id)
        quantity = int(request.POST.get('quantity', 1))

        if variant.stock >= quantity:
            variant.stock -= quantity
            variant.save()

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

from django.db.models import Q

def brand_management(request):
    search_query = request.GET.get('search', '')  
    
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        if name:
            Brand.objects.create(name=name, description=description)
            messages.success(request, "Brand added successfully!")
            return redirect("brand_management")
        else:
            messages.error(request, "Brand name is required.")
    
    if search_query:
        brands = Brand.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
    else:
        brands = Brand.objects.all()

    paginator = Paginator(brands, 10)  
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
        "page_obj": page_obj,  
        "search_query": search_query  
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



# admin coupon management

def coupon_list(request):
    search_query = request.GET.get('search', '')  
    coupons = Coupon.objects.all()

    if search_query:
        coupons = coupons.filter(code__icontains=search_query) 

    if request.method == 'POST':
        code = request.POST.get('code')
        discount_percentage = request.POST.get('discount_percentage')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'

        Coupon.objects.create(code=code, discount_percentage=discount_percentage, description=description, is_active=is_active)
        messages.success(request, 'Coupon created successfully!')

    return render(request, 'coupon_management.html', {'coupons': coupons, 'search_query': search_query})

# Delete a coupon
def delete_coupon(request, coupon_id):
    coupon = Coupon.objects.get(id=coupon_id)
    coupon.delete()
    messages.success(request, 'Coupon deleted successfully!')
    return redirect('coupon_list')


def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        
        try:
            coupon = Coupon.objects.get(code=code, is_active=True, used=False)  
            coupon.mark_as_used()  
            messages.success(request, "Coupon applied successfully!")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid or expired coupon.")

    return redirect('checkout_page')



def manage_offers(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    search_query = request.GET.get('search', '')

    if search_query:
        offers = Offer.objects.filter(name__icontains=search_query) 
    else:
        offers = Offer.objects.all()

    paginator = Paginator(offers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    offers_with_details = []
    for offer in page_obj:
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
        offer_id = request.POST.get('offer_id', None)
        name = request.POST.get('name')
        discount_percentage = request.POST.get('discount_percentage')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        offer_type = request.POST.get('offer_type')
        products_selected = request.POST.getlist('products')
        categories_selected = request.POST.getlist('categories')
        referral_code = request.POST.get('referral_code', '')

        if not name or not discount_percentage or not start_date or not end_date or not offer_type:
            messages.error(request, "All fields are required.")
            return redirect('manage_offers')

        try:
            if offer_id:  
                offer = Offer.objects.get(id=offer_id)
                offer.name = name
                offer.discount_percentage = discount_percentage
                offer.start_date = start_date
                offer.end_date = end_date
                offer.offer_type = offer_type

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
            else:  
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
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return redirect('manage_offers')

    return render(request, 'offer_management.html', {
        'offers_with_products': offers_with_details,
        'products': products,
        'categories': categories,
        'page_obj': page_obj,
        'search_query': search_query,  
    })


def delete_offer(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)
    offer.delete()
    messages.success(request, "Offer deleted successfully!")
    return redirect('manage_offers')




#admin dashboard  ( not finished demo )
def dashboard_view(request):
    total_sales = Order.objects.filter(status='Delivered').aggregate(total_sales=Sum('total_price'))['total_sales'] or 0
    
    total_orders = Order.objects.count()
    
    delivered_orders = Order.objects.filter(status='Delivered').count()
    
    cancelled_orders = Order.objects.filter(status='Cancelled').count()
    
    total_discount = 0
    offers = Offer.objects.filter(end_date__gte=timezone.now())  
    coupons = Coupon.objects.filter(is_active=True)  
    for offer in offers:
        total_discount += offer.discount_percentage
    for coupon in coupons:
        total_discount += coupon.discount_percentage
    
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    deactivated_products = Product.objects.filter(is_active=False).count()

    total_categories = Category.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()
    deactivated_categories = Category.objects.filter(is_active=False).count()

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



@login_required
def sales_report(request):
    date_filter = request.GET.get('date_filter', 'today')
    search_query = request.GET.get('search', '')

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
    else:
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')
        if start_date_str and end_date_str:
            start_date = timezone.make_aware(datetime.combine(datetime.strptime(start_date_str, '%Y-%m-%d'), datetime.min.time()))
            end_date = timezone.make_aware(datetime.combine(datetime.strptime(end_date_str, '%Y-%m-%d'), datetime.max.time()))
        else:
            start_date = end_date = None

    selected_statuses = request.GET.getlist('status_filter')

    orders = Order.objects.all().order_by('-created_at')
    if start_date and end_date:
        orders = orders.filter(created_at__range=[start_date, end_date])

    if selected_statuses:
        orders = orders.filter(status__in=selected_statuses)

    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) |  
            Q(user__username__icontains=search_query) | 
            Q(user__email__icontains=search_query) | 
            Q(variant__product__name__icontains=search_query) 
        ).distinct()

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        orders = orders.filter(total_price__gte=float(min_price))
    if max_price:
        orders = orders.filter(total_price__lte=float(max_price))

    if request.GET.get('offer_applied', ''):
        orders = orders.filter(offer_discount__gt=0)
    if request.GET.get('coupon_applied', ''):
        orders = orders.filter(coupon_discount__gt=0)

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    non_canceled_orders = orders.exclude(status='Cancelled')
    total_sales = non_canceled_orders.aggregate(total_sales=Sum('total_price'))['total_sales'] or 0
    total_orders = non_canceled_orders.count()
    total_discount = non_canceled_orders.aggregate(
        total_discount=Sum(F('offer_discount') + F('coupon_discount'))
    )['total_discount'] or 0
    average_order_value = total_sales / total_orders if total_orders > 0 else 0

    is_pdf = request.GET.get('pdf', False)

    context = {
        'orders': page_obj,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_discount': total_discount,
        'average_order_value': round(average_order_value, 2),
        'date_filter': date_filter,
        'selected_statuses': selected_statuses,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'available_statuses': [
            ('Pending', 'Pending'),
            ('Processing', 'Processing'),
            ('Shipped', 'Shipped'),
            ('Out for Delivery', 'Out for Delivery'),
            ('Delivered', 'Delivered'),
            ('Cancelled', 'Cancelled'),
            ('Return Pending', 'Return Pending'),
            ('Return Accepted', 'Return Accepted'),
        ],
        'is_pdf': is_pdf,
    }

    return render(request, 'sales_report.html', context)


#to excel
def export_to_excel(request):
    orders = Order.objects.all()
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Sales Report'
    
    ws.append(['Order ID', 'Date', 'Customer', 'Items', 'Subtotal', 'Offer Discount', 'Final Amount', 'Status'])
    
    for order in orders:
        items = ', '.join([str(item.product_id) for item in order.items.all()]) 
        
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
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'
    wb.save(response)
    
    return response



def export_to_pdf(request):
    date_filter = request.GET.get('date_filter', 'today')
    start_date = None
    end_date = None
    status_filter = request.GET.getlist('status_filter', [])

    heading = "Sales Report"  

    if date_filter == 'today':
        today = datetime.today()
        start_date = timezone.make_aware(datetime.combine(today, datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(today, datetime.max.time()))
        heading = f"Sales Report for {today.strftime('%d %B %Y')}" 
    elif date_filter == 'this_week':
        today = datetime.today()
        start_date = timezone.make_aware(datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(today + timedelta(days=(6 - today.weekday())), datetime.max.time()))
        heading = "Sales Report for the Week"  
    elif date_filter == 'this_month':
        today = datetime.today()
        start_date = timezone.make_aware(datetime.combine(today.replace(day=1), datetime.min.time()))
        end_date = timezone.make_aware(datetime.combine(today.replace(day=1) + timedelta(days=32), datetime.min.time()) - timedelta(seconds=1))
        heading = f"Sales Report for {today.strftime('%B %Y')}"
    elif date_filter == 'custom':
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')
        if start_date_str and end_date_str:
            start_date = timezone.make_aware(datetime.combine(datetime.strptime(start_date_str, '%Y-%m-%d'), datetime.min.time()))
            end_date = timezone.make_aware(datetime.combine(datetime.strptime(end_date_str, '%Y-%m-%d'), datetime.max.time()))
            heading = f"Sales Report from {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')}" 


    orders = Order.objects.all()
    if start_date and end_date:
        orders = orders.filter(created_at__range=[start_date, end_date])
    if status_filter:
        orders = orders.filter(status__in=status_filter)

    buffer = BytesIO()

    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    table_data = [
        ["Order ID", "Date", "Customer", "Items", "Subtotal", "Offer/Coupon", "Offer Discount", "Final Amount"]
    ]

    total_subtotal = 0
    total_offer_discount = 0
    total_final_amount = 0

    styles = getSampleStyleSheet()
    item_style = ParagraphStyle(name="ItemStyle", fontSize=10, leading=12, wordWrap='CJK')

    for order in orders:
        items = Paragraph(", ".join([str(item.product.name) for item in order.items.all()]), item_style)
        offer_coupon = order.offer_or_coupon
        offer_discount = order.offer_discount + order.coupon_discount
        final_amount = order.discounted_price

        total_subtotal += order.subtotal
        total_offer_discount += offer_discount
        total_final_amount += final_amount

        table_data.append([
            str(order.id),
            order.created_at.strftime("%Y-%m-%d"),
            order.user.username,
            items, 
            f"{order.subtotal:.2f}", 
            offer_coupon,
            f"{offer_discount:.2f}",  
            f"{final_amount:.2f}" 
        ])

    table_data.append([
        "Total",
        "",
        "",
        "",
        f"{total_subtotal:.2f}",
        "",
        f"{total_offer_discount:.2f}",
        f"{total_final_amount:.2f}"
    ])

    table = Table(table_data, colWidths=[45, 60, 80, 110, 50, 75, 80, 80])  

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),        # Header row background
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),    # Header row text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),                # Center align all cells
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),        # Header row font
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),                     # Header row padding
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),          # Table body background
        ('GRID', (0, 0), (-1, -1), 1, colors.black),        # Add grid lines
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),                      # Align text to the top of the row
        # Styling the total row
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),    # Total row background
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),       # Total row font
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),         # Total row text color
        ('ALIGN', (0, -1), (-1, -1), 'CENTER'),               # Center align total row
    ])

    table.setStyle(style)

    title_style = styles['Title']
    title_style.fontName = 'Helvetica-Bold'
    title_style.fontSize = 16
    title_style.spaceAfter = 12
    title = Paragraph(heading, title_style)

    elements = [title, Spacer(1, 12), table]
    pdf.build(elements)

    pdf_content = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    return response
