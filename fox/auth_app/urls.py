
from django.urls import path
from . import views


urlpatterns = [
    #url for authentications
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.main_page, name='home'),  # Home page for regular users
    path('admin_home/', views.admin_home, name='admin_home'),  # Admin-specific page
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),

 
    

]



