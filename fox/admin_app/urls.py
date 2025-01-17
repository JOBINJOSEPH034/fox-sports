
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views 

urlpatterns = [
    #url for admin home page
    path('admin_home',views.admin_home,name='admin_home'),

    #url for admin product functions
    path('product',views.product_list,name='product'),
    path('product/add_product',views.add_product,name='add_product'),
    path('product/edit/<int:product_id>/',views.edit_product,name='edit_product'),
    path('product/toggle/<int:product_id>/', views.toggle_product_status, name='toggle_product_status'), #for soft delete
    path('product/<int:product_id>/variants/', views.product_variant_list, name='product_variant_list'),
    path('product/permanent_delete/<int:product_id>/', views.permanent_delete_product, name='delete_product'),


    #url for admin customer functions
    path('customer',views.customer_list,name='customer'),
    path('customer/edit_customer',views.edit_customer,name='edit_customer'),
    path('customers/<int:user_id>/block/', views.block_user, name='block_user'),
    path('customers/<int:user_id>/unblock/', views.unblock_user, name='unblock_user'),


    #url for admin category functions
    path('category',views.category_list,name='category'),
    path('category/add_category',views.add_category,name='add_category'),
    path('edit_category',views.edit_category,name='edit_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('category/toggle/<int:category_id>/', views.toggle_category_status, name='toggle_category_status'),  #for soft delete

    #ur for admin order management
    path('admin_order-management/', views.admin_order_management, name='admin_order_management'),
    path('order/<int:order_id>/status/<str:status>/', views.admin_update_order_status, name='admin_update_order_status'),
    path('order/<int:order_id>/cancel/', views.admin_cancel_order, name='admin_cancel_order'),

    #url for admin inventry management
    path('inventory/', views.inventory_management, name='inventory_management'),
    path('create_order/<int:product_id>/', views.create_order, name='create_order'),
    path('create_order/<int:product_id>/<int:variant_id>/', views.create_order, name='create_order_variant'),  
    path('update_variant_stock/<int:variant_id>/', views.update_variant_stock, name='update_variant_stock'),


 path('inventory/', views.inventory_management, name='inventory_management'),
    path('update_stock/<int:product_id>/', views.update_stock_for_product, name='update_stock_for_product'),
    path('update_variant_stock/<int:product_id>/', views.update_variant_stock, name='update_variant_stock'),

    #url for brand management
    path('brand-management/', views.brand_management, name='brand_management'),
    path('brand-management/delete/<int:brand_id>/', views.delete_brand, name='delete_brand'),
    path('brand-management/deactivate/<int:brand_id>/', views.deactivate_brand, name='deactivate_brand'),
    path('brand-management/toggle-status/<int:brand_id>/', views.toggle_brand_status, name='toggle_brand_status'),



    path('coupons/', views.coupon_list, name='coupon_list'),
    path('coupons/delete/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),


    path('manage-offers/', views.manage_offers, name='manage_offers'),
    path('delete-offer/<int:offer_id>/', views.delete_offer, name='delete_offer'),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)