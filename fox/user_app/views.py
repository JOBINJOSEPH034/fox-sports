from django.shortcuts import render ,redirect,get_object_or_404
from admin_app.models import Category ,Product,ProductVariant,Brand
from .models import Cart, CartItem,Address, Order,OrderItem
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.http import JsonResponse





# Create your views here.

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
    featured_products=Product.objects.filter(stock__gt=0,is_active=True)[:8]   # Showing the first 6 products

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
    products = Product.objects.filter(stock__gt=0,is_active=True) 

    cart_items = CartItem.objects.filter(user=request.user)
    total_items = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0
   
    search_query = request.GET.get('search', '').strip()
    selected_category = request.GET.get('category')
    selected_brand = request.GET.get('brand')
    sort_option = request.GET.get('sort')
    # Search functionality
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    # Filter by category
    if selected_category:
        products = products.filter(category_id=selected_category)

    if selected_brand:
        products = products.filter(brand_id=selected_brand)    


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
    
    
    return render(request,'shop.html',{
        'categories': categories,
        'products': products,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_brand': selected_brand,
        'sort_option': sort_option,
        'total_items': total_items

    })


@login_required
def shop_men(request):
    categories = Category.objects.filter(is_active=True)
    men_category = get_object_or_404(Category, name="Men")
    products = Product.objects.filter(category=men_category, stock__gt=0, is_active=True)

    cart_items = CartItem.objects.filter(user=request.user)
    total_items = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0

    search_query = request.GET.get('search', '').strip()
    sort_option = request.GET.get('sort')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    
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
        


    return render(request, 'shop_men.html', {
        'products': products,
        'categories': categories,
        'total_items': total_items,
        'search_query': search_query,
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
    sort_option = request.GET.get('sort')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    
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
        


    return render(request, 'shop_women.html', {
        'products': products,
        'categories': categories,
        'total_items': total_items,
        'search_query': search_query,
        'sort_option': sort_option,
        
        })



@login_required
@never_cache
def product_detail(request,product_id):
    product = Product.objects.get(id=product_id)
    is_out_of_stock = product.stock == 0
    variants = product.variants.all()  # Fetch variants for this product

    return render(request, 'detail.html', {
        'product': product,
        'is_out_of_stock': is_out_of_stock,
        'variants': variants,  
    
    })



@login_required
def cart_page(request):
    # Get the cart for the logged-in user
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Get all cart items
    cart_items = CartItem.objects.filter(cart=cart)

    # Calculate the total price of the cart
    cart_total = sum(item.total_price for item in cart_items)
    total_items = cart_items.aggregate(total_items=Sum('quantity'))['total_items'] or 0
    
    # Pass the cart items and total to the template
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'total_items': total_items,
    })





@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variant_id = request.POST.get('variant')  # Variant is optional
    quantity = int(request.POST.get('quantity', 1))

    # Get or create the user's cart
    cart, _ = Cart.objects.get_or_create(user=request.user)

    # Handle variant if it exists
    variant = ProductVariant.objects.filter(id=variant_id).first() if variant_id else None

    # Check if the item is already in the cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': quantity}
    )

    # If item exists, update the quantity
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
        cart_item.delete()  # Delete the item from the cart
        return redirect('cart_page')  # Redirect back to the cart page
    except CartItem.DoesNotExist:
        # Handle the case where the item doesn't exist (optional)
        return redirect('cart_page')  # Or return an error page
    




@login_required
def manage_addresses(request):
    
    if request.method == 'POST':
        # Add or update address manually
        address_id = request.POST.get('address_id')
        if address_id:  # Update existing address
            address = get_object_or_404(Address, id=address_id, user=request.user)
            address.name = request.POST.get('name')
            address.phone = request.POST.get('phone')
            address.address_line = request.POST.get('address_line')
            address.city = request.POST.get('city')
            address.state = request.POST.get('state')
            address.postal_code = request.POST.get('postal_code')
            address.is_default = request.POST.get('is_default') == 'on'
            address.save()
        else:  # Create a new address
            Address.objects.create(
                user=request.user,
                name=request.POST.get('name'),
                phone=request.POST.get('phone'),
                address_line=request.POST.get('address_line'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                postal_code=request.POST.get('postal_code'),
                is_default=request.POST.get('is_default') == 'on'
            )
        return redirect('manage_addresses')

    # Display all addresses for the user
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'manage_addresses.html', {'addresses': addresses})


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        # Handle address editing logic
        address.name = request.POST['name']
        address.phone = request.POST['phone']
        address.address_line = request.POST['address_line']
        address.city = request.POST['city']
        address.state = request.POST['state']
        address.postal_code = request.POST['postal_code']

        # Check if the 'default' option was selected
        is_default = request.POST.get('is_default') == 'on'
        if is_default:
            # Unset other default addresses
            Address.objects.filter(user=request.user).update(is_default=False)
        address.is_default = is_default
        address.save()
        return redirect('manage_addresses')  # After editing, redirect to the manage addresses page

    return render(request, 'edit_address.html', {'address': address})



@login_required
def delete_address(request, address_id):
    # Delete an address
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    return redirect('profile')




#chechout

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    cart_total = sum(item.total_price for item in cart_items)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty. Please add items to your cart before checking out.")
        return redirect('shop')  # Replace with your actual shop page URL name

    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        address_id = request.POST.get('selected_address')
        selected_address = get_object_or_404(Address, id=address_id, user=request.user)

        # Create the order
        order = Order.objects.create(
            user=request.user,
            address=selected_address,
            total_price=cart_total,
        )

        # Iterate through cart items and create individual order items
        for item in cart_items:
            # Check if the cart item has a product variant
            if item.variant:
                # Update stock for the product variant
                if item.variant.stock >= item.quantity:
                    item.variant.stock -= item.quantity  # Reduce the stock by the ordered quantity
                    item.variant.save()  # Save the updated variant stock
                    OrderItem.objects.create(
                        order=order,
                        product=item.variant.product,
                        variant=item.variant,
                        quantity=item.quantity,
                        total_price=item.total_price
                    )
                else:
                    messages.error(request, f"Insufficient stock for {item.variant.name}.")
                    return redirect('checkout')  # Redirect back to checkout page if stock is insufficient
            else:
                # Update stock for the product if no variant
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity  # Reduce the stock by the ordered quantity
                    item.product.save()  # Save the updated product stock
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        total_price=item.total_price
                    )
                else:
                    messages.error(request, f"Insufficient stock for {item.product.name}.")
                    return redirect('checkout')  # Redirect back to checkout page if stock is insufficient

        # Clear cart after order is placed
        cart_items.delete()

        # Redirect to the order success page with the order ID
        return redirect('order_success', order_id=order.id)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'addresses': addresses,
    })
@login_required
def order_success(request, order_id):
    # Display order confirmation
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_success.html', {'order': order})







#order management for user
@login_required
def is_admin(user):
    return user.is_superuser

@login_required
def order_management(request):
    # Fetch all orders for the logged-in user, ordered by creation date (latest first)
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
            # Update the user model fields
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')

            # If you have a Profile model with additional fields, update that as well
            if hasattr(user, 'profile'):
                user.profile.phone = request.POST.get('phone')
                user.profile.bio = request.POST.get('bio', '')

            # Save the updated user and profile
            user.save()
            if hasattr(user, 'profile'):
                user.profile.save()

            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')  # Redirect to the same page after saving
        except Exception as e:
            messages.error(request, f"Error occurred: {e}")
            return redirect('profile')

    return render(request, 'profile/profile.html', {
        'user': user
    })