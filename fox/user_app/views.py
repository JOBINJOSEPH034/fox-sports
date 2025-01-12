from django.shortcuts import render ,redirect,get_object_or_404
from admin_app.models import Category ,Product,ProductVariant,Brand
from .models import Cart, CartItem,Address, Order,OrderItem
from django.http import JsonResponse
from django.template.loader import render_to_string

from django.core.paginator import Paginator
from django.db.models import Sum
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Q

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


#USER HOME PAGE
@never_cache
def home_page(request):
    categories=Category.objects.all()
    featured_products=Product.objects.filter(stock__gt=0)[:6] 
    
    return render(request,'home.html',{
        'categories':categories,
        'featured_products':featured_products

    })

@login_required
@never_cache
def main_page(request):

    categories=Category.objects.filter(is_active=True)
    featured_products=Product.objects.filter(stock__gt=0,is_active=True)[:8]   

    cart_items = CartItem.objects.filter(user=request.user)
    total_items = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0

    return render(request,'main.html',{
        'categories':categories,
        'featured_products':featured_products,
        'total_items': total_items,
    })
        
def main_page_search(request):
    query = request.GET.get('search', '').strip()
    if query:
        try:
            product = Product.objects.get(name__icontains=query)
            return redirect('product_detail', product.id)
        except Product.DoesNotExist:
            return render(request, 'main.html', {'error': 'Product not found!'})
    return render(request, 'main.html')
        
# USER PRODUCT PAGE
@login_required
@never_cache
def product_page(request):
    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(stock__gt=0, is_active=True)

    cart_items = CartItem.objects.filter(user=request.user)
    total_items = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0

    search_query = request.GET.get('search', '').strip()
    selected_categories = request.GET.getlist('category')  # Multi-select for categories
    selected_brands = request.GET.getlist('brand')  # Multi-select for brands
    sort_option = request.GET.get('sort')

    # Search functionality
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filter by selected categories
    if selected_categories:
        products = products.filter(category_id__in=selected_categories)

    # Filter by selected brands
    if selected_brands:
        products = products.filter(brand_id__in=selected_brands)

    brands = Brand.objects.all()

    # Sorting functionality
    if sort_option:
        if sort_option == 'low_to_high':
            products = products.order_by('price')
        elif sort_option == 'high_to_low':
            products = products.order_by('-price')
        elif sort_option == 'alphabetical':
            products = products.order_by('name')
        elif sort_option == 'reverse_alphabetical':
            products = products.order_by('-name')
        elif sort_option == 'popularity':
            products = products.order_by('-popularity')  # Assuming popularity is a field in Product
        elif sort_option == 'new_arrivals':
            products = products.order_by('-created_at')  # Assuming created_at is a field in Product

    # Pagination logic
    paginator = Paginator(products, 9)  # Show 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop.html', {
        'categories': categories,
        'products': page_obj,  # Pass paginated products to the template
        'search_query': search_query,
        'selected_categories': selected_categories,
        'selected_brands': selected_brands,
        'sort_option': sort_option,
        'brands': brands,
        'total_items': total_items,
        'page_obj': page_obj  # Pass page_obj for pagination
    })



@login_required
def shop_men(request):
    categories = Category.objects.filter(is_active=True)
    men_category = get_object_or_404(Category, name="Men")
    products = Product.objects.filter(category=men_category, stock__gt=0, is_active=True)

    cart_items = CartItem.objects.filter(user=request.user)
    total_items = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0

    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by category and brand
    selected_categories = request.GET.getlist('category')
    selected_brands = request.GET.getlist('brand')
    if selected_categories:
        products = products.filter(category_id__in=selected_categories)
    if selected_brands:
        products = products.filter(brand_id__in=selected_brands)

    # Sorting functionality
    sort_option = request.GET.get('sort')
    if sort_option:
        if sort_option == 'low_to_high':
            products = products.order_by('price')
        elif sort_option == 'high_to_low':
            products = products.order_by('-price')
        elif sort_option == 'alphabetical':
            products = products.order_by('name')
        elif sort_option == 'reverse_alphabetical':
            products = products.order_by('-name')
        elif sort_option == 'popularity':
            products = products.order_by('-popularity')
        elif sort_option == 'new_arrivals':
            products = products.order_by('-created_at')

    # Pagination setup
    paginator = Paginator(products, 9)  # Show 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    brands = Brand.objects.all()

    return render(request, 'shop_men.html', {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'total_items': total_items,
        'search_query': search_query,
        'selected_categories': selected_categories,  # Pass selected categories
        'selected_brands': selected_brands,          # Pass selected brands
        'sort_option': sort_option,
    })


@login_required
def shop_women(request):
    categories = Category.objects.filter(is_active=True)
    women_category = get_object_or_404(Category, name="Women")
    products = Product.objects.filter(category=women_category, stock__gt=0, is_active=True)

    cart_items = CartItem.objects.filter(user=request.user)
    total_items = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0

    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by category and brand
    selected_categories = request.GET.getlist('category')
    selected_brands = request.GET.getlist('brand')
    if selected_categories:
        products = products.filter(category_id__in=selected_categories)
    if selected_brands:
        products = products.filter(brand_id__in=selected_brands)

    # Sorting functionality
    sort_option = request.GET.get('sort')
    if sort_option:
        if sort_option == 'low_to_high':
            products = products.order_by('price')
        elif sort_option == 'high_to_low':
            products = products.order_by('-price')
        elif sort_option == 'alphabetical':
            products = products.order_by('name')
        elif sort_option == 'reverse_alphabetical':
            products = products.order_by('-name')
        elif sort_option == 'popularity':
            products = products.order_by('-popularity')
        elif sort_option == 'new_arrivals':
            products = products.order_by('-created_at')

    # Pagination setup
    paginator = Paginator(products, 9)  # Show 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    brands = Brand.objects.all()

    return render(request, 'shop_women.html', {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'total_items': total_items,
        'search_query': search_query,
        'selected_categories': selected_categories,  # Pass selected categories
        'selected_brands': selected_brands,          # Pass selected brands
        'sort_option': sort_option,
    })



@login_required
@never_cache
def product_details(request,product_id):
    product = Product.objects.get(id=product_id)
    is_out_of_stock = product.stock == 0
    variants = product.variants.all()  # not

    return render(request, 'detail.html', {
        'product': product,
        'is_out_of_stock': is_out_of_stock,
        'variants': variants,  
    
    })



@login_required
def cart_page(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    cart_total = sum(item.total_price for item in cart_items)
    total_items = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'total_items': total_items,
    })





@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variant_id = request.POST.get('variant') 
    quantity = int(request.POST.get('quantity', 1))
    cart, _ = Cart.objects.get_or_create(user=request.user)
    variant = ProductVariant.objects.filter(id=variant_id).first() if variant_id else None
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    messages.success(request, f"{product.name} added to cart!")
    return redirect('cart_page')




@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart_page')

def remove_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()  
        return redirect('cart_page')  
    except CartItem.DoesNotExist:
        return redirect('cart_page')  
    



# Manage Addresses View
@login_required
def manage_addresses(request):
    if request.method == 'POST':
        # Handle Add/Edit Address logic
        address_id = request.POST.get('address_id')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address_line = request.POST.get('address_line')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        is_default = request.POST.get('is_default') == 'on'

        if address_id:  # Editing existing address
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:  # Adding new address
            address = Address(user=request.user)

        # Update the address details
        address.name = name
        address.phone = phone
        address.address_line = address_line
        address.city = city
        address.state = state
        address.postal_code = postal_code
        address.is_default = is_default

        if is_default:
            Address.objects.filter(user=request.user).update(is_default=False)

        address.save()

        return redirect('manage_addresses')

    addresses = Address.objects.filter(user=request.user)
    return render(request, "profile/addresses.html", {"addresses": addresses})

@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        address.name = request.POST['name']
        address.phone = request.POST['phone']
        address.address_line = request.POST['address_line']
        address.city = request.POST['city']
        address.state = request.POST['state']
        address.postal_code = request.POST['postal_code']
        address.is_default = 'is_default' in request.POST
        address.save()
        return redirect('manage_addresses')
    return render(request, 'profile/addresses.html', {'address': address})


@login_required
def get_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    return JsonResponse({
        'id': address.id,
        'name': address.name,
        'phone': address.phone,
        'address_line': address.address_line,
        'city': address.city,
        'state': address.state,
        'postal_code': address.postal_code,
        "is_default": address.is_default,

    })


@login_required
def update_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        try:
            # Debugging print statements
            print("Received POST data:", request.POST)

            address.name = request.POST.get('name')
            address.phone = request.POST.get('phone')
            address.address_line = request.POST.get('address_line')
            address.city = request.POST.get('city')
            address.state = request.POST.get('state')
            address.postal_code = request.POST.get('postal_code')
            address.save()

            # Check if the data was saved
            print(f"Updated Address: {address.name}, {address.phone}, {address.address_line}")

            return JsonResponse({
                'success': True,
                'id': address.id,
                'name': address.name,
                'phone': address.phone,
                'address_line': address.address_line,
                'city': address.city,
                'state': address.state,
                'postal_code': address.postal_code,
            })
        except Exception as e:
            # Handle any unexpected errors
            print("Error:", str(e))
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    return redirect('manage_addresses')

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    cart_total = sum(item.total_price for item in cart_items)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty. Please add items to your cart before checking out.")
        return redirect('shop')

    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        print(request.POST)
        address_id = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method')
        
        if not address_id:
            messages.error(request, "Please select an address.")
            return redirect('checkout')

        selected_address = get_object_or_404(Address, id=address_id, user=request.user)

        order = Order.objects.create(
            user=request.user,
            address=selected_address,
            total_price=cart_total,
            payment_method=payment_method
        )

        for item in cart_items:
            try:
                order_item = OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variant=item.variant,
                    quantity=item.quantity,
                    total_price=item.total_price
                )
                order_item.reduce_stock()
            except ValueError as e:
                messages.error(request, f"Stock error for {item.product.name}: {str(e)}")
                order.delete()  
                return redirect('checkout')
        
        # Clear the cart after order creation
        cart_items.delete()

        # Redirect to order success page
        return redirect('order_success', order_id=order.id)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'addresses': addresses,
    })



#display order sucess messg 
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_success.html', {'order': order})



#order management for user
@login_required
def order_management(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'profile/orders.html', {'orders': orders})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status in ['Pending', 'Processing', 'Shipped','Out for Delivery']:
        order.status = 'Cancelled'
        order.save()
        messages.success(request, f"Order {order.id} has been successfully canceled and stock has been updated.")
    else:
        messages.error(request, f"Order {order.id} cannot be canceled.")

    return redirect('order_management')



# User Profile View (Displays user details)
@login_required
def profile(request):
    user = request.user

    if request.method == 'POST':
        try:
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')

            if hasattr(user, 'profile'):
                user.profile.phone = request.POST.get('phone')
                user.profile.bio = request.POST.get('bio', '')

            user.save()
            if hasattr(user, 'profile'):
                user.profile.save()

            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile') 
        except Exception as e:
            messages.error(request, f"Error occurred: {e}")
            return redirect('profile')

    return render(request, 'profile/profile.html', {
        'user': user
    })