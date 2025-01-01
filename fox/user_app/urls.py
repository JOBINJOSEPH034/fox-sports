
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
urlpatterns = [
    #url for user 
    path('',views.home_page ),
    path('main/',views.main_page,name='main'),
    path('shop',views.product_page,name='shop'),
    path('detail',views.product_detail,name='detail'),
    
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),
    path('edit-address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove_item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),


    path('manage-addresses/', views.manage_addresses, name='manage_addresses'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
   
    

    
    
]
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)