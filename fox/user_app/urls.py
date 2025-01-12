
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
    path('men/', views.shop_men, name='shop_men'),
    path('women/', views.shop_women, name='shop_women'),
    
    #for cart
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path('edit-address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove_item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),

    #addrss management
    path('manage-addresses/', views.manage_addresses, name='manage_addresses'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('checkout/', views.checkout, name='checkout'),
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
    path('addresses/<int:address_id>/',views.get_address, name='get_address'),
    path('addresses/<int:address_id>/edit/',views.update_address, name='update_address'),



    path('edit-address/<int:address_id>/', views.edit_address, name='edit_address'),




]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)