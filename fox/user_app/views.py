

import razorpay 

import json
from django.shortcuts import render ,redirect,get_object_or_404
from admin_app.models import Category ,Product,ProductVariant,Brand,Coupon
from .models import Cart, CartItem,Address, Order,OrderItem,Wishlist,OrderReturn,Wallet,Transaction
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils.timezone import now
from django.db.models import Q
from django.http import Http404


from django.conf import settings

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

from decimal import Decimal
import random
import uuid


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
    selected_categories = request.GET.getlist('category')  
    selected_brands = request.GET.getlist('brand')  
    sort_option = request.GET.get('sort')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if selected_categories:
        products = products.filter(category_id__in=selected_categories)

    if selected_brands:
        products = products.filter(brand_id__in=selected_brands)

    brands = Brand.objects.all()

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

    # Pagination 
    paginator = Paginator(products, 9)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop.html', {
        'categories': categories,
        'products': page_obj,  
        'search_query': search_query,
        'selected_categories': selected_categories,
        'selected_brands': selected_brands,
        'sort_option': sort_option,
        'brands': brands,
        'total_items': total_items,
        'page_obj': page_obj  
    })



@login_required
def shop_men(request):
    categories = Category.objects.filter(is_active=True)
    men_category = get_object_or_404(Category, name="Men")
    products = Product.objects.filter(category=men_category, stock__gt=0, is_active=True)

    cart_items = CartItem.objects.filter(user=request.user)
    total_items = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0

    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    selected_categories = request.GET.getlist('category')
    selected_brands = request.GET.getlist('brand')
    if selected_categories:
        products = products.filter(category_id__in=selected_categories)
    if selected_brands:
        products = products.filter(brand_id__in=selected_brands)

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

    paginator = Paginator(products, 9)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    brands = Brand.objects.all()

    return render(request, 'shop_men.html', {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'total_items': total_items,
        'search_query': search_query,
        'selected_categories': selected_categories,  
        'selected_brands': selected_brands,          
        'sort_option': sort_option,
    })


@login_required
def shop_women(request):
    categories = Category.objects.filter(is_active=True)
    women_category = get_object_or_404(Category, name="Women")
    products = Product.objects.filter(category=women_category, stock__gt=0, is_active=True)

    cart_items = CartItem.objects.filter(user=request.user)
    total_items = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0

    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    

    selected_categories = request.GET.getlist('category')
    selected_brands = request.GET.getlist('brand')
    if selected_categories:
        products = products.filter(category_id__in=selected_categories)
    if selected_brands:
        products = products.filter(brand_id__in=selected_brands)


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

    paginator = Paginator(products, 9)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    brands = Brand.objects.all()

    return render(request, 'shop_women.html', {
        'products': page_obj,
        'categories': categories,
        'brands': brands,
        'total_items': total_items,
        'search_query': search_query,
        'selected_categories': selected_categories,  
        'selected_brands': selected_brands,          
        'sort_option': sort_option,
    })



@login_required
@never_cache
def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    is_out_of_stock = product.stock == 0
    variants = product.variants.all()  # Add your variants logic here

    # Check if the product is in the user's wishlist
    is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    return render(request, 'detail.html', {
        'product': product,
        'is_out_of_stock': is_out_of_stock,
        'variants': variants,
        'is_in_wishlist': is_in_wishlist  # Pass this variable to the template
    })



@login_required
def cart_page(request):
    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    # Calculate the cart total
    cart_total = sum(item.total_price for item in cart_items)
    total_items = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0

    # Initialize discount and final total
    discount_amount = 0
    final_total = cart_total
    coupon_code = None

    # Check if a coupon is applied and handle coupon removal
    if cart.applied_coupon:
        coupon = cart.applied_coupon
        discount_amount = (cart_total * coupon.discount_percentage) / 100
        final_total = cart_total - discount_amount
        coupon_code = coupon.code

    # Handle coupon application
    if request.method == 'POST':
        if 'coupon_code' in request.POST:
            coupon_code = request.POST.get('coupon_code')
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                cart.applied_coupon = coupon  # Apply the coupon to the cart
                cart.save()
                discount_amount = (cart_total * coupon.discount_percentage) / 100
                final_total = cart_total - discount_amount
                messages.success(request, f'Coupon applied! You get {coupon.discount_percentage}% off.')
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid or expired coupon code.')
        
        # Handle coupon removal
        if 'remove_coupon' in request.POST:
            cart.applied_coupon = None  # Remove the coupon from the cart
            cart.save()
            discount_amount = 0
            final_total = cart_total
            coupon_code = None
            messages.success(request, 'Coupon removed successfully.')

        return redirect('cart_page')  # Redirect to the same cart page to update the coupon details

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'total_items': total_items,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'coupon_code': coupon_code,  # Pass the coupon code to the template
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
def apply_coupon(request):
    if request.method == "POST":
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code')

        try:
            coupon = Coupon.objects.get(code=coupon_code)
            cart = Cart.objects.get(user=request.user)
            cart.applied_coupon = coupon
            cart.save()

            # Calculate discount
            discount_amount = cart.total_price * coupon.discount_percentage / 100
            final_total = cart.total_price - discount_amount

            return JsonResponse({'success': True, 'coupon_code': coupon_code, 'final_total': final_total})

        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid coupon code.'})

@login_required
def remove_coupon(request):
    if request.method == "POST":
        cart = Cart.objects.get(user=request.user)
        cart.applied_coupon = None
        cart.save()

        # Recalculate total without discount
        final_total = cart.total_price  # Adjust if any other logic for final total is needed

        return JsonResponse({'success': True, 'final_total': final_total})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@login_required

def update_cart_item(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    
    # Get the updated quantity from the form
    new_quantity = int(request.POST.get('quantity'))

    # Prevent quantity from going below 1
    if new_quantity < 1:
        new_quantity = 1
    
    # Update the cart item with the new quantity
    cart_item.quantity = new_quantity
    cart_item.save()

    return redirect('cart_page')


def remove_cart_item(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()  
        return redirect('cart_page')  
    except CartItem.DoesNotExist:
        return redirect('cart_page')  
    



# Manage Addresses View(profile)
@login_required
def manage_addresses(request):
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address_line = request.POST.get('address_line')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        is_default = request.POST.get('is_default') == 'on'

        if address_id:  
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:  
            address = Address(user=request.user)

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
            address.name = request.POST.get('name')
            address.phone = request.POST.get('phone')
            address.address_line = request.POST.get('address_line')
            address.city = request.POST.get('city')
            address.state = request.POST.get('state')
            address.postal_code = request.POST.get('postal_code')
            address.save()

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
    addresses = Address.objects.filter(user=request.user)

    # Coupon-related calculations
    coupon_code = cart.applied_coupon.code if cart.applied_coupon else None
    discount_amount = 0
    if cart.applied_coupon:
        discount_amount = (cart_total * cart.applied_coupon.discount_percentage) / 100

    final_total = cart_total - discount_amount

    # Razorpay Client Initialization
    razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = razorpay_client.order.create({
        'amount': int(final_total * 100),  # Amount in paise
        'currency': 'INR',
        'payment_capture': '1'
    })

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        address_id = request.POST.get('selected_address')

        if not address_id:
            messages.error(request, "Please select an address.")
            return redirect('checkout')

        selected_address = get_object_or_404(Address, id=address_id, user=request.user)

        if payment_method == 'razorpay':
            return JsonResponse({'order_id': razorpay_order['id'], 'final_total': final_total})

        elif payment_method == 'cod':
            # Handle COD payment
            order = Order.objects.create(
                user=request.user,
                address=selected_address,
                total_price=final_total,
                payment_method='cod'
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variant=item.variant,
                    quantity=item.quantity,
                    total_price=item.total_price
                )
            cart_items.delete()
            messages.success(request, "Order placed successfully!")
            return redirect('order_success', order_id=order.id)

        elif payment_method == 'wallet':
            wallet = Wallet.objects.get(user=request.user)
            if wallet.balance < Decimal(final_total):
                messages.error(request, "Insufficient wallet balance.")
                return redirect('checkout')

            wallet.balance -= Decimal(final_total)
            wallet.save()

            order = Order.objects.create(
                user=request.user,
                address=selected_address,
                total_price=final_total,
                payment_method='wallet'
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    variant=item.variant,
                    quantity=item.quantity,
                    total_price=item.total_price
                )
            cart_items.delete()
            messages.success(request, "Order placed successfully using wallet!")
            return redirect('order_success', order_id=order.id)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'final_total': final_total,
        'discount_amount': discount_amount,
        'coupon_code': coupon_code,
        'addresses': addresses,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
         'final_total_in_paise': final_total * 100,
    })


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def verify_payment(request):
    data = json.loads(request.body)
    razorpay_payment_id = data['razorpay_payment_id']
    razorpay_order_id = data['razorpay_order_id']
    razorpay_signature = data['razorpay_signature']
    address_id = data['address_id']

    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        selected_address = Address.objects.get(id=address_id)

        order = Order.objects.create(
            user=request.user,
            address=selected_address,
            total_price=data['final_total'],
            payment_method='razorpay',
            payment_id=razorpay_payment_id
        )
        return JsonResponse({'success': True, 'order_id': order.id})
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'success': False})











#display order sucess messg 
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_success.html', {'order': order})


def order_management(request):
    # Get all orders
    orders = Order.objects.all()
    
    # Set up pagination
    paginator = Paginator(orders, 10)  # Show 10 orders per page
    page_number = request.GET.get('page')  # Get the page number from the request
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'profile/orders.html', {'page_obj': page_obj})

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


@login_required
def request_return(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        reason = request.POST.get('reason')
        additional_comments = request.POST.get('additional_comments')
        
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            if order.status == 'Delivered':
                # Create a return request
                OrderReturn.objects.create(order=order, reason=reason, additional_comments=additional_comments)
                order.status = 'Return Pending'
                order.return_requested_at = now()
                order.save()
                return JsonResponse({'message': 'Return request has been submitted successfully.', 'status': 'success'})
            else:
                return JsonResponse({'message': 'Return is not allowed for this order.', 'status': 'error'})
        except Order.DoesNotExist:
            return JsonResponse({'message': 'Order not found.', 'status': 'error'})
    
    return JsonResponse({'message': 'Invalid request.', 'status': 'error'})



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


@login_required
def wishlist_view(request):
    # Fetch the wishlist items for the logged-in user
    wishlist = Wishlist.objects.filter(user=request.user)

    # Pass the wishlist to the template
    return render(request, 'profile/wishlist.html', {'wishlist': wishlist})


@login_required
def add_to_cart_from_wishlist(request, wishlist_item_id):
    # Get the wishlist item by ID
    wishlist_item = Wishlist.objects.get(id=wishlist_item_id)

    # Get the associated product from the wishlist item
    product = wishlist_item.product

    # Check if the user already has a cart, or create a new one
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the product already exists in the cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    # If the product is already in the cart, update the quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # Redirect to the cart page or wherever you want
    return redirect('cart:cart_detail')

def remove_from_wishlist(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.filter(user=request.user, product=product).delete()
        return redirect('wishlist_view')  # Replace with the name of your wishlist view
    except Http404:
        # If the product doesn't exist, optionally display a message or handle it
        return redirect('wishlist_view')  # Or show an error page



@login_required
def toggle_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    user = request.user

    # Check if the product is already in the user's wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)

    if not created:
        # If the item already exists, remove it from the wishlist
        wishlist_item.delete()
        added = False
    else:
        added = True

    # Return JSON response indicating the action
    return JsonResponse({'added': added})

def add_to_wishlist(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        user = request.user
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        
        # Add product to wishlist if it's not already there
        if product not in wishlist.products.all():
            wishlist.products.add(product)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Product already in wishlist'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def remove_from_wishlist(request, id):  # Matches <int:id> in URL pattern
    wishlist_item = Wishlist.objects.get(id=id, user=request.user)
    wishlist_item.delete()
    return redirect('wishlist')


@login_required
def wallet_page(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all().order_by('-created_at')

    if request.method == 'POST':
        action = request.POST.get('action')
        amount = request.POST.get('amount')

        try:
            # Ensure amount is properly converted to a Decimal to match Wallet's balance
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")
            
            if action == 'add':
                wallet.balance += amount
                transaction_type = 'deposit'
            elif action == 'withdraw':
                if amount > wallet.balance:
                    messages.error(request, "Insufficient balance.")
                    return redirect('wallet_page')
                wallet.balance -= amount
                transaction_type = 'withdraw'
            else:
                messages.error(request, "Invalid transaction type.")
                return redirect('wallet_page')

            wallet.save()

            # Creating a transaction with a properly generated transaction ID
            Transaction.objects.create(
                wallet=wallet,
                transaction_id=str(uuid.uuid4()),  # Generate a unique transaction ID
                type=transaction_type,
                amount=amount,
            )
            messages.success(request, f"{action.capitalize()} successful!")
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('wallet_page')

    return render(request, 'profile/wallet_page.html', {
        'wallet': wallet,
        'transactions': transactions,
    })


