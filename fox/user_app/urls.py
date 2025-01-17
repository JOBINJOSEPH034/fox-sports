
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
urlpatterns = [
    
    #url for user 
    path('',views.home_page ),
    path('main/',views.main_page,name='main'),
    path('shop',views.product_page,name='shop'),
     path('product/<int:product_id>/', views.product_details, name='product_details'), 
    path('toggle_wishlist/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('men/', views.shop_men, name='shop_men'),
    path('women/', views.shop_women, name='shop_women'),
    
    #for cart
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path('edit-address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove_item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),

    #checkout
    path('checkout/', views.checkout, name='checkout'),


    #addrss management
    path('manage-addresses/', views.manage_addresses, name='manage_addresses'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    
   
    path('profile/', views.profile, name='profile'),
    path('order-management/', views.order_management, name='order_management'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    #change passwod (default)
    path(
        'change-password/',
        PasswordChangeView.as_view(
            template_name='profile/change_password.html',
            success_url=reverse_lazy('profile')  
        ),
        name='change_password'
    ),

    #profile address url
    path('addresses/<int:address_id>/',views.get_address, name='get_address'),
    path('addresses/<int:address_id>/edit/',views.update_address, name='update_address'),
    path('edit-address/<int:address_id>/', views.edit_address, name='edit_address'),


    path('wishlist/', views.wishlist_view, name='wishlist'),
   path('wishlist/add_to_cart/<int:wishlist_item_id>/', views.add_to_cart_from_wishlist, name='add_to_cart_from_wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:id>/', views.remove_from_wishlist, name='remove_from_wishlist'),




    path('wallet/', views.wallet_page, name='wallet_page'), 

  path('request-return/', views.request_return, name='request_return'),


   path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'), 


]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)