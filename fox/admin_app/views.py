from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from . models import Category,Product,Brand,ProductVariant
from user_app.models import Order
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import json
from django.http import HttpResponse
from django.http import JsonResponse

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


@login_required
@never_cache

def add_product(request):
    print("Inside the add_product view") 
    if request.method == "POST":
        try:
            # Create the new product
            name = request.POST.get('name')
            description = request.POST.get('description')
            category = Category.objects.get(id=request.POST.get('category'))
            stock = request.POST.get('stock')
            brand, _ = Brand.objects.get_or_create(name=request.POST.get('brand'))
            price = request.POST.get('price')
            image1 = request.FILES.get('image1')
            image2 = request.FILES.get('image2')

            # Save the product
            product = Product.objects.create(
                name=name,
                description=description,
                category=category,
                stock=stock,
                brand=brand,
                price=price,
                image1=image1,
                image2=image2,
            )

            # Process product variants
            variants_json = request.POST.get('variants_data')  # Expecting a JSON string
            print(f"Received variants data: {variants_json}")
            if variants_json:
                variants = json.loads(variants_json)  # Parse JSON data
                print(f"Parsed variants: {variants}")
                for variant in variants:
                    print(f"Saving variant: {variant}")
                    ProductVariant.objects.create(
                        product=product,
                        size=variant['size'],
                        additional_price=variant['additional_price'],
                    )
            else:
                print("No variants data found!")        

            messages.success(request, "Product added successfully!")
            return redirect('add_product') 

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('add_product') 

    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'add-product.html', {'categories': categories, 'brands': brands})

      

@login_required
@never_cache
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        try:
            # Update product fields
            product.name = request.POST.get('name')
            product.description = request.POST.get('description')
            product.category = Category.objects.get(id=request.POST.get('category'))
            product.stock = request.POST.get('stock')
            product.brand, _ = Brand.objects.get_or_create(name=request.POST.get('brand'))
            product.price = request.POST.get('price')
            product.image1 = request.FILES.get('image1') or product.image1
            product.image2 = request.FILES.get('image2') or product.image2
            product.save()

            # Process product variants
            variants_json = request.POST.get('variants_data')  # Expecting a JSON string
            if variants_json:
                variants = json.loads(variants_json)  # Parse JSON data
                product.variants.all().delete()  # Clear existing variants for the product
                for variant in variants:
                    ProductVariant.objects.create(
                        product=product,
                        size=variant['size'],
                        additional_price=variant['additional_price'],
                    )

            messages.success(request, "Product updated successfully!")
            return redirect('edit_product', product_id=product.id) 

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('edit_product', product_id=product.id)

    categories = Category.objects.all()
    variants = product.variants.all()  # Get existing variants
    return render(
        request, 
        'edit-product.html', 
        {'product': product, 'categories': categories, 'variants': variants}
    )









#for soft delete
def toggle_product_status(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = not product.is_active  # Toggle the status
    product.save()
    status = "activated" if product.is_active else "soft deleted"
    messages.success(request, f"Product '{product.name}' has been {status}.")
    return redirect('product')


def permanent_delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()  # Permanently delete the product from the database
        messages.success(request, "Product permanently deleted.")
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
    
    return redirect('product')  # Redirect back to the product list page

@login_required
@never_cache
def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = product.variants.all()  # Fetch associated variants
    base_price = product.price
    total_price = {}

 # Calculate the total price for each variant
    for variant in variants:
        total_price[variant.id] = base_price + variant.price_difference


    return render(request, 'detail.html', {
        'product': product,
        'variants': variants,
        'total_price': total_price
    })




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
def admin_order_management(request):
    orders = Order.objects.all().select_related('product','variant')  # You can filter by user if needed
    return render(request, 'admin_order.html', {'orders': orders})



def admin_update_order_status(request, order_id, status):
    # Get the order object by its ID
    order = get_object_or_404(Order, id=order_id)

    # Update the order status
    order.status = status
    order.save()

    # Redirect back to the order management page
    return redirect('admin_order_management')  # Adjust the URL name accordingly



def admin_cancel_order(request, order_id):
    # Get the order object by its ID (without user restriction for admin)
    order = get_object_or_404(Order, id=order_id)
    print(f"Canceling order {order.id} with current status: {order.status}")

    if order.status in ['Pending', 'Processing', 'Shipped','Out for Delivery']:
    

        # Change the order status to cancelled
        order.status = 'Cancelled'
        order.save()

        messages.success(request, f"Order {order.id} has been successfully canceled and stock updated.")
    else:
        messages.error(request, f"Order {order.id} cannot be canceled.")

    # Redirect to the order management page
    return redirect('admin_order_management')


# View to display inventory
def inventory_management(request):
    products = Product.objects.all()
   
    return render(request, 'inventory_management.html', {
        'products': products,
    
    })

# Update stock for products
def update_stock(request, product_id, variant_id=None):
    if variant_id:
        # Handle variant stock update
        variant = get_object_or_404(ProductVariant, id=variant_id)
        if request.method == 'POST':
            new_stock = int(request.POST.get('stock', variant.stock))
            variant.stock = new_stock
            variant.save()
            messages.success(request, f"Stock updated for variant: {variant.name}")
        return redirect('inventory_management')
    else:
        # Handle product stock update
        product = get_object_or_404(Product, id=product_id)
        if request.method == 'POST':
            new_stock = int(request.POST.get('stock', product.stock))
            product.stock = new_stock
            product.save()
            messages.success(request, f"Stock updated for product: {product.name}")
        return redirect('inventory_management')



# Update stock for variants
def update_variant_stock(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    if request.method == 'POST':
        new_stock = int(request.POST.get('stock', variant.stock))
        variant.stock = new_stock
        variant.save()
    return redirect('inventory_management')

# Order Creation for Products
def create_order(request, product_id, variant_id=None):
    if variant_id:
        # Handle order for a variant
        variant = get_object_or_404(ProductVariant, id=variant_id)
        quantity = int(request.POST.get('quantity', 1))

        if variant.stock >= quantity:
            variant.stock -= quantity
            variant.save()
            Order.objects.create(
                user=request.user, 
                product=variant.product,  # Correct product assignment
                variant=variant,  # Assign the variant
                quantity=quantity,
                total_price=variant.product.price * quantity  # Calculate total price
            )
            messages.success(request, f"Order placed for variant: {variant.name}")
        else:
            messages.error(request, f"Insufficient stock for variant: {variant.name}")
        return redirect('product_detail', variant.product.id)
    else:
        # Handle order for a product
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        if product.stock >= quantity:
            product.stock -= quantity
            product.save()
            Order.objects.create(
                user=request.user, 
                product=product,  # Correct product assignment
                quantity=quantity,
                total_price=product.price * quantity  # Calculate total price
            )
            messages.success(request, f"Order placed for product: {product.name}")
        else:
            messages.error(request, f"Insufficient stock for product: {product.name}")
        return redirect('product_detail', product.id)


def create_order_with_variant(request, variant_id):
    variant = ProductVariant.objects.get(id=variant_id)
    quantity = int(request.POST.get('quantity', 1))

    # Check if the variant has enough stock
    if variant.stock >= quantity:
        # Reduce the stock of the variant
        variant.stock -= quantity
        variant.save()

        # Create the order
        Order.objects.create(user=request.user, product=variant.product, quantity=quantity)

        messages.success(request, f"Order placed successfully for {variant.product.name} ({variant.name})!")
    else:
        messages.error(request, f"Insufficient stock for {variant.product.name} ({variant.name}).")

    return redirect('product_detail', variant.product.id)