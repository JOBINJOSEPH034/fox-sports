
from datetime import timedelta
from time import timezone
import uuid
import razorpay 
import json
from django.shortcuts import render ,redirect,get_object_or_404
from admin_app.models import Category ,Product,ProductVariant,Brand,Coupon,Offer
from .models import Cart, CartItem,Address, Order,OrderItem, Transaction, Wallet,Wishlist,OrderReturn
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils.timezone import now
from django.db.models import Q
from django.http import Http404
from django.conf import settings
from decimal import Decimal
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from json.decoder import JSONDecodeError
from django.db import transaction






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
    variants = product.variants.all()

    is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    today = now().date()

    product_offers = Offer.objects.filter(
        offer_type=Offer.PRODUCT,
        products=product,
        start_date__lte=today,
        end_date__gte=today
    )

    category_offers = Offer.objects.filter(
        offer_type=Offer.CATEGORY,
        categories=product.category,
        start_date__lte=today,
        end_date__gte=today
    )

    best_offer = None
    if product_offers.exists():
        best_offer = product_offers.order_by('-discount_percentage').first()
    elif category_offers.exists():
        best_offer = category_offers.order_by('-discount_percentage').first()

    discounted_price = None
    if best_offer:
        discount = (product.price * best_offer.discount_percentage) / 100
        discounted_price = round(product.price - discount, 2)

    variant_offers = {}
    for variant in variants:
        variant_price = variant.total_price
        variant_discounted_price = variant_price
        if best_offer:
            variant_discount = (variant_price * best_offer.discount_percentage) / 100
            variant_discounted_price = max(0, round(variant_price - variant_discount, 2))  # No negative prices

        variant_offers[variant.id] = {
            'variant_price': variant_price,
            'variant_discounted_price': variant_discounted_price,
            'offer_name': best_offer.name if best_offer else None,
        }

    return render(request, 'detail.html', {
        'product': product,
        'is_out_of_stock': is_out_of_stock,
        'variants': variants,
        'is_in_wishlist': is_in_wishlist,
        'best_offer': best_offer,
        'discounted_price': discounted_price,
        'variant_offers': variant_offers,  # Pass the dictionary
    })

    
@login_required
def cart_page(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    for item in cart_items:
        if item.variant and item.variant.stock is not None:
            if item.quantity > item.variant.stock:
                item.quantity = item.variant.stock
                item.save()
                messages.warning(
                    request, 
                    f"The quantity of {item.variant.product.name} has been adjusted to available stock ({item.variant.stock})."
                )
        else:
            messages.warning(
                request, 
                f"Stock for {item.product.name} is unavailable or variant data is missing."
            )

    cart_total = sum(item.total_price for item in cart_items)
    total_items = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0

    discount_amount = 0
    final_total = cart_total
    coupon_code = None

    available_coupons = Coupon.objects.filter(is_active=True, used=False).exclude(used_orders__user=request.user)

    if cart.applied_coupon:
        coupon = cart.applied_coupon
        discount_amount = (cart_total * coupon.discount_percentage) / 100
        final_total = cart_total - discount_amount
        coupon_code = coupon.code

    if request.method == 'POST':
        if 'update_quantity' in request.POST:
            cart_item_id = request.POST.get('cart_item_id')
            new_quantity = int(request.POST.get('quantity'))
            try:
                cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
                if new_quantity > cart_item.variant.stock:
                    messages.error(
                        request, 
                        f"Cannot add more than available stock ({cart_item.variant.stock}) for {cart_item.variant.product.name}."
                    )
                else:
                    cart_item.quantity = new_quantity
                    cart_item.save()
                    cart_total = sum(item.total_price for item in cart_items)
                    final_total = cart_total - discount_amount
                    messages.success(request, f"Quantity updated for {cart_item.variant.product.name}.")
            except CartItem.DoesNotExist:
                messages.error(request, "Cart item not found.")

        elif 'coupon_code' in request.POST:
            coupon_code = request.POST.get('coupon_code')
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True, used=False)
                cart.applied_coupon = coupon
                cart.save()
                discount_amount = (cart_total * coupon.discount_percentage) / 100
                final_total = cart_total - discount_amount
                messages.success(request, f"Coupon {coupon_code} applied successfully!")
            except Coupon.DoesNotExist:
                messages.error(request, "Invalid or expired coupon code.")
        
        elif 'remove_coupon' in request.POST:
            if cart.applied_coupon:
                cart.applied_coupon = None
                cart.save()
                discount_amount = 0
                final_total = cart_total
                messages.success(request, "Coupon removed successfully.")
            else:
                messages.error(request, "No coupon applied to remove.")

        return redirect('cart_page')

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'total_items': total_items,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'coupon_code': coupon_code,
        'available_coupons': available_coupons,
    })



@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variant_id = request.POST.get("variant")  
    quantity = int(request.POST.get("quantity", 1))

    variant = None
    if variant_id and variant_id.isdigit():  
        variant = ProductVariant.objects.filter(id=int(variant_id)).first()

    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={"quantity": quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    messages.success(request, f"{product.name} added to cart!")
    return redirect("cart_page")

#coupon in cart page
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
        final_total = cart.total_price     

        return JsonResponse({'success': True, 'final_total': final_total})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



@login_required
def update_cart_item(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    new_quantity = int(request.POST.get('quantity'))

    if new_quantity < 1:
        new_quantity = 1
    
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
    order_id = request.GET.get('order_id')
    existing_order = None

    if order_id:
        existing_order = get_object_or_404(Order, id=order_id, user=request.user)

    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    cart_total = sum(item.total_price for item in cart_items)

    addresses = Address.objects.filter(user=request.user)

    coupon_code = cart.applied_coupon.code if cart.applied_coupon else None
    discount_amount = (cart_total * cart.applied_coupon.discount_percentage) / 100 if cart.applied_coupon else 0

    delivery_charge = 0  
    selected_address = addresses.first() if addresses.exists() else None

    if selected_address:
        delivery_charge = (
            50 if selected_address.state == "Kerala" else
            120 if selected_address.state == "Tamil Nadu" else
            150 if selected_address.state == "Karnataka" else
            180
        )

    for item in cart_items:
        if item.variant.stock < item.quantity:
            messages.error(request, f"Not enough stock for {item.variant.product.name}. Please adjust the quantity or remove the item.")
            return redirect('cart') 

    if request.method == 'POST':
        address_id = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method')

        if not address_id:
            messages.error(request, "Please select an address.")
            return redirect('checkout')

        selected_address = get_object_or_404(Address, id=address_id, user=request.user)

        delivery_charge = (
            50 if selected_address.state == "Kerala" else
            120 if selected_address.state == "Tamil Nadu" else
            150 if selected_address.state == "Karnataka" else
            180
        )

        final_total = cart_total - discount_amount + delivery_charge

        if payment_method == 'cod' and cart_total > 1000:
            messages.error(request, "COD is not available for orders above ₹1000. Please use Wallet or Online Payment.")
            return redirect('checkout')

        if payment_method == 'wallet':
            wallet_balance = request.user.wallet.balance
            if wallet_balance < final_total:
                messages.error(request, "Insufficient wallet balance. Please use another payment method.")
                return redirect('checkout')

        if existing_order:
            order = existing_order
            order.total_price = final_total
            order.payment_method = payment_method
            order.status = "Pending"
            order.save()
        else:
            order = Order.objects.create(
                user=request.user,
                address=selected_address,
                total_price=final_total,
                subtotal=cart_total,
                discount_percentage=cart.applied_coupon.discount_percentage if cart.applied_coupon else 0,
                coupon_discount=discount_amount,
                delivery_charge=delivery_charge,
                payment_method=payment_method,
                status="Pending"
            )

        if not existing_order:
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.variant.product,
                    variant=item.variant,
                    quantity=item.quantity,
                    total_price=item.total_price
                )

        if cart.applied_coupon:
            order.coupons.add(cart.applied_coupon)
            cart.applied_coupon.used = True  # Mark the coupon as used
            cart.applied_coupon.save()
            
        if payment_method == "wallet":
            wallet = request.user.wallet
            wallet.balance -= Decimal(final_total)
            wallet.save()

        cart_items.delete()
        cart.applied_coupon = None
        cart.save()

        if payment_method == "wallet" or payment_method == "cod":
            messages.success(request, f"Order placed successfully using {payment_method}!")
            return redirect("order_success", order_id=order.id)

        if payment_method != "cod":
            try:
                razorpay_order = razorpay_client.order.create({
                    "amount": int(final_total * 100),  
                    "currency": "INR",
                    "payment_capture": "1"
                })

                razorpay_order_id = razorpay_order["id"]
                order.razorpay_order_id = razorpay_order_id
                order.save()

                if razorpay_order['status'] == 'captured':
                    for item in cart_items:
                        item.variant.stock -= item.quantity
                        item.variant.save()

                    messages.success(request, f"Order placed successfully using {payment_method}!")
                    order.status = "pending"
                    order.save()
                    return redirect("order_success", order_id=order.id)
                else:
                    for item in cart_items:
                        item.variant.stock += item.quantity
                        item.variant.save()

                    messages.error(request, "Payment failed. Please try again.")
                    order.status = "Payment Failed"
                    order.save()
                    return redirect("order_management")

            except Exception as e:
                for item in cart_items:
                    item.variant.stock += item.quantity
                    item.variant.save()

                messages.error(request, "Payment failed. Please try again.")
                order.status = "Payment Failed"
                order.save()
                return redirect("order_management")

    final_total = cart_total - discount_amount + delivery_charge
    final_total_in_paise = int(final_total * 100)

    wallet_balance = request.user.wallet.balance if hasattr(request.user, 'wallet') else 0
    wallet_disabled = wallet_balance < final_total

    try:
        razorpay_order = razorpay_client.order.create({
            "amount": final_total_in_paise,
            "currency": "INR",
            "payment_capture": "1"
        })
        razorpay_order_id = razorpay_order["id"]
    except Exception as e:
        razorpay_order_id = None
        messages.error(request, "Failed to initialize payment gateway. Please try again.")

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "cart_total": cart_total,
        "final_total": final_total,
        "discount_amount": discount_amount,
        "coupon_code": coupon_code,
        "addresses": addresses,
        "selected_address": selected_address,
        "razorpay_order_id": razorpay_order_id,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "final_total_in_paise": final_total_in_paise,
        "wallet_balance": wallet_balance,
        "wallet_disabled": wallet_disabled,
        "delivery_charge": delivery_charge
    })



     
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def verify_payment(request):
    data = json.loads(request.body)
    payment_method = data['payment_method']
    address_id = data['address_id']
    selected_address = Address.objects.get(id=address_id)

    if payment_method == 'razorpay':
        razorpay_payment_id = data['razorpay_payment_id']
        razorpay_order_id = data['razorpay_order_id']
        razorpay_signature = data['razorpay_signature']

        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            order = Order.objects.create(
                user=request.user,
                address=selected_address,
                total_price=data['final_total'],
                payment_method='razorpay',
                payment_id=razorpay_payment_id,
                status='Pending'
            )

            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.variant.product,
                    variant=item.variant,
                    quantity=item.quantity,
                    total_price=item.total_price
                )
                item.variant.stock -= item.quantity
                item.variant.save()

            cart_items.delete()

            return JsonResponse({'success': True, 'order_id': order.id})

        except razorpay.errors.SignatureVerificationError:
            # Payment failed
            order = Order.objects.create(
                user=request.user,
                address=selected_address,
                total_price=data['final_total'],
                payment_method='razorpay',
                status='Payment Pending',
                payment_failed_at=timezone.now()
            )
            return JsonResponse({'success': False, 'message': 'Payment failed. Please try again.'})

    else:
        order = Order.objects.create(
            user=request.user,
            address=selected_address,
            total_price=data['final_total'],
            payment_method=payment_method,
            status='Pending'
        )

        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.variant.product,
                variant=item.variant,
                quantity=item.quantity,
                total_price=item.total_price
            )
            item.variant.stock -= item.quantity
            item.variant.save()

        cart_items.delete()

        return JsonResponse({'success': True, 'order_id': order.id})
    
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@csrf_exempt
def payment_failed(request):
    if request.method == 'POST':
        try:
            try:
                data = json.loads(request.body)
            except JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)

            error_code = data.get('error_code')
            error_description = data.get('error_description')
            address_id = data.get('address_id')
            payment_method = data.get('payment_method')
            final_total = data.get('final_total')

            if not all([address_id, payment_method, final_total]):
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

            selected_address = get_object_or_404(Address, id=address_id, user=request.user)

            order = Order.objects.create(
                user=request.user,
                address=selected_address,
                total_price=final_total,
                payment_method=payment_method,
                status='Payment Pending',  
                payment_failed_at=timezone.now()
            )

            cart = Cart.objects.filter(user=request.user).first()
            if not cart:
                return JsonResponse({'success': False, 'error': 'Cart not found'}, status=404)

            cart_items = CartItem.objects.filter(cart=cart)
            if not cart_items.exists():
                return JsonResponse({'success': False, 'error': 'No items in cart'}, status=400)

            for item in cart_items:
                if not item.variant:
                    return JsonResponse({'success': False, 'error': 'Invalid product variant'}, status=400)

                OrderItem.objects.create(
                    order=order,
                    product=item.variant.product,
                    variant=item.variant,
                    quantity=item.quantity,
                    total_price=item.total_price
                )
                item.variant.stock -= item.quantity
                item.variant.save()

            cart_items.delete()

            return JsonResponse({'success': True, 'order_id': order.id})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST' and 'download_invoice' in request.POST:
        return generate_invoice(request, order)

    return render(request, 'order_success.html', {'order': order})

def generate_invoice(request, order):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{order.id}.pdf'

    doc = SimpleDocTemplate(response, pagesize=letter)

    styles = getSampleStyleSheet()

    elements = []

    title = f"Invoice - Order #{order.id}"
    title_paragraph = Paragraph(title, styles['Title'])
    elements.append(title_paragraph)

    elements.append(Paragraph("<br/>", styles['Normal']))

    order_info = f"""
        <b>Order ID:</b> {order.id}<br/>
        <b>Total Amount:</b> ₹{order.total_price}<br/>
        <b>Date:</b> {order.created_at.strftime('%d/%m/%Y')}<br/>
        <b>Shipping Address:</b> {order.address}<br/>
        <b>Payment Method:</b> {order.payment_method}<br/><br/>
    """
    order_info_paragraph = Paragraph(order_info, styles['Normal'])
    elements.append(order_info_paragraph)

    items_list = "<b>Ordered Items:</b><br/>"
    
    for item in order.items.all():
        items_list += f"{item.product.name} - Quantity: {item.quantity} - Total: ₹{item.total_price}<br/>"
    
    items_paragraph = Paragraph(items_list, styles['Normal'])
    elements.append(items_paragraph)

    total_info = f"""
        <b>Total Amount:</b> ₹{order.total_price}<br/>
        <b>Tax (10%):</b> ₹{order.total_price * 0.1}<br/>
        <b>Grand Total:</b> ₹{order.total_price + (order.total_price * 0.1)}<br/><br/>
    """
    total_info_paragraph = Paragraph(total_info, styles['Normal'])
    elements.append(total_info_paragraph)

    continue_shopping_paragraph = Paragraph('<a href="/shop/">Continue Shopping</a>', styles['Normal'])
    elements.append(continue_shopping_paragraph)

    doc.build(elements)

    return response


@login_required
def order_management(request):
    order_items = OrderItem.objects.filter(
        order__user=request.user
    ).select_related(
        'order', 'variant', 'variant__product'
    ).order_by('-order__created_at')
    
    for item in order_items:
        delivered_timestamp = item.order.delivered_at
        has_return = OrderReturn.objects.filter(order_item=item).exists()
        
        if delivered_timestamp and not has_return:
            return_deadline = delivered_timestamp + timedelta(days=7)
            item.can_return = (
                item.status == 'Delivered' and 
                timezone.now() <= return_deadline
            )
        else:
            item.can_return = False
            
        if item.order.status == 'Payment Failed':
            payment_failed_at = item.order.payment_failed_at
            if payment_failed_at:
                retry_deadline = payment_failed_at + timedelta(days=7)
                item.can_retry_payment = timezone.now() <= retry_deadline
            else:
                item.can_retry_payment = False
        else:
            item.can_retry_payment = False
    
    paginator = Paginator(order_items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'profile/orders.html', {
        'page_obj': page_obj, })

@login_required
def cancel_order_item(request, order_item_id):
    order_item = get_object_or_404(
        OrderItem, 
        id=order_item_id, 
        order__user=request.user
    )
    
    cancellable_statuses = [
        'Payment Failed', 'Pending', 'Processing', 
        'Shipped', 'Out for Delivery', 'Payment Pending'
    ]
    
    try:
        with transaction.atomic():
            if order_item.status in cancellable_statuses:
                if order_item.variant:
                    order_item.variant.stock += order_item.quantity
                    order_item.variant.save()

                refund_amount = order_item.total_price
                if order_item.order.payment_method in ['online', 'wallet','cod']:
                        wallet, created = Wallet.objects.get_or_create(user=request.user)
                        wallet.balance+=Decimal(str(refund_amount))
                        wallet.save()

                        Transaction.objects.create(
                        wallet=wallet,
                        transaction_id=f"RF{str(uuid.uuid4())[:8].upper()}",
                        type='deposit',
                        amount=refund_amount,
                        description=f"Refund for order item #{order_item.id}"
                    )    
                
                OrderItem.objects.filter(id=order_item.id).update(status='Cancelled')
                
                remaining_active = OrderItem.objects.filter(
                    order=order_item.order
                ).exclude(
                    status__in=['Cancelled', 'Return Accepted']
                ).exists()
                
                if not remaining_active:
                    order = order_item.order
                    order.status = 'Cancelled'
                    order.save()
                    

                messages.success(request, "Order cancelled successfully.")
            else:
                messages.error(request, 
                    "This order cannot be cancelled in its current status."
                )
                
    except Exception:
        messages.error(request, "Error cancelling order.")
    
    return redirect('order_management')




@login_required
def continue_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == "Payment Pending":
        order_items = OrderItem.objects.filter(order=order)
        cart, created = Cart.objects.get_or_create(user=request.user)

        for item in order_items:
            CartItem.objects.create(
                user=request.user,
                cart=cart,
                product=item.variant.product,
                variant=item.variant,  
                quantity=item.quantity
            )
        
        order.status = "Payment Failed"
        order.save()

        messages.info(request, "Your failed order items have been added back to your cart. Please complete the payment to proceed.")

    return redirect('checkout')





@login_required
def request_return(request):
    if request.method == 'POST':
        order_item_id = request.POST.get('order_item_id')
        reason = request.POST.get('reason')
        additional_comments = request.POST.get('additional_comments')
        image = request.FILES.get('image')
        
        try:
            with transaction.atomic():
                order_item = OrderItem.objects.select_related('order').get(
                    id=order_item_id, 
                    order__user=request.user
                )

                if order_item.status != 'Delivered':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'This item has not been delivered yet'
                    })

                if OrderReturn.objects.filter(order_item=order_item).exists():
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Return already requested for this item'
                    })

                return_request = OrderReturn.objects.create(
                    order=order_item.order,
                    order_item=order_item,
                    reason=reason,
                    additional_comments=additional_comments,
                    image=image,
                    status='Return Pending',
                    return_requested_at=timezone.now(),
                    return_quantity=1
                )

                refund_amount = order_item.total_price
                
                if order_item.order.payment_method in ['online', 'wallet', 'cod']:
                    wallet, created = Wallet.objects.get_or_create(user=request.user)
                    wallet.balance += Decimal(str(refund_amount))
                    wallet.save()

                    Transaction.objects.create(
                        wallet=wallet,
                        transaction_id=f"RF{str(uuid.uuid4())[:8].upper()}",
                        type='deposit',
                        amount=refund_amount,
                        description=f"Refund for returned item #{order_item.id}"
                    )

                OrderItem.objects.filter(id=order_item.id).update(
                    status='Return Accepted',
                    is_refunded=True
                )

                remaining_active = OrderItem.objects.filter(
                    order=order_item.order
                ).exclude(
                    status__in=['Cancelled', 'Return Accepted']
                ).exists()

                if not remaining_active:
                    Order.objects.filter(id=order_item.order.id).update(status='Return Accepted')

                return JsonResponse({
                    'status': 'success',
                    'message': 'Return request submitted and refund processed successfully'
                })

        except OrderItem.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Order item not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    })
   
@login_required
def mark_as_delivered(request, order_id):
    try:
        with transaction.atomic():
            order = Order.objects.get(id=order_id)
            order_items = OrderItem.objects.filter(order=order)
            
            for item in order_items:
                if item.status != 'Cancelled':
                    item.status = 'Delivered'
                    item.save()
            
            order.status = 'Delivered'
            order.delivered_at = now()
            order.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Order marked as delivered'
            })
    except Order.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Order not found'
        })
    
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
                user.profile.date_of_birth = request.POST.get('date_of_birth')
                
                if 'profile_picture' in request.FILES:
                    user.profile.profile_picture = request.FILES['profile_picture']

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
    wishlist = Wishlist.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(wishlist, 5)  
    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number) 

    return render(request, 'profile/wishlist.html', {'page_obj': page_obj})

#from cart
@login_required
def add_to_cart_from_wishlist(request, wishlist_item_id):
  
    wishlist_item = Wishlist.objects.get(id=wishlist_item_id)
    product = wishlist_item.product
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart:cart_detail')

def remove_from_wishlist(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.filter(user=request.user, product=product).delete()
        return redirect('wishlist_view')  
    except Http404:
      
        return redirect('wishlist_view')  #


@login_required
def toggle_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    user = request.user
    wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)

    if not created:
       
        wishlist_item.delete()
        added = False
    else:
        added = True

    return JsonResponse({'added': added})

def add_to_wishlist(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        user = request.user
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        
        if product not in wishlist.products.all():
            wishlist.products.add(product)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Product already in wishlist'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def remove_from_wishlist(request, id): 
    wishlist_item = Wishlist.objects.get(id=id, user=request.user)
    wishlist_item.delete()
    return redirect('wishlist')



def wallet_page(request):
    user_wallet = request.user.wallet  
    transactions = user_wallet.transactions.all().order_by('-created_at')

    paginator = Paginator(transactions, 8)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'profile/wallet_page.html', {
        'wallet': user_wallet,
        'transactions': page_obj,  
        'razorpay_key': settings.RAZORPAY_KEY_ID
    })

@csrf_exempt
def create_razorpay_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        amount = int(data.get("amount", 0)) * 100  
        if amount <= 0:
            return JsonResponse({"status": "error", "message": "Invalid amount."}, status=400)
        
        try:
            order = razorpay_client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1
            })
            return JsonResponse({
                "status": "success",
                "order_id": order["id"],
                "amount": amount,
                "currency": "INR"
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)

@csrf_exempt
def verify_wallet_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        payment_id = data.get("razorpay_payment_id")
        order_id = data.get("razorpay_order_id")
        signature = data.get("razorpay_signature") 
        amount = Decimal(data.get("amount", 0))  

        try:
            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature  
            })

            user_wallet = request.user.wallet
            user_wallet.balance += amount  
            user_wallet.save()

            user_wallet.transactions.create(
                transaction_id=payment_id,
                amount=amount,
                type="add"
            )

            return JsonResponse({"status": "success", "message": "Wallet updated."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)




@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        data = json.loads(request.body)
        new_status = data.get('status')

        if new_status:
            order.status = new_status
            order.save()
            return JsonResponse({'success': True})
        
    return JsonResponse({'success': False}, status=400)
