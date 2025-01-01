
from django.shortcuts import render,redirect
from . models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail
from django.core.cache import cache
from django.urls import reverse

from django.conf import settings
import random
import re



@never_cache
#login view
def login_page(request):
    
    if request.method =='POST':
        username=request.POST.get('name')
        password=request.POST.get("password")
        if not username or not password:
            messages.error(request, 'Both username and password are required!')
            return render(request, 'accounts/login.html')
        user = authenticate(request,username=username,password=password)
        
        if user is not None:
            if user.is_active:
                login(request,user)
                request.session['username'] = user.username 
                messages.success(request, f"Welcome {user.username}!")
        
                if user.is_superuser:
                    return redirect('admin_home')
                else:
                    return redirect('main')
            else:
                messages.error(request, 'Your account has been blocked. Please contact support.')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request,'accounts/login.html')            
        
    


@never_cache
#signup view
def signup(request):
    if request.method=='POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        user_name=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')


        if not first_name or not last_name or not user_name or not email or not password or not confirm_password:
            messages.error(request, 'All fields are required!')
            return redirect('signup')

       
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('signup')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long!')
            return redirect('signup')
        
        if not re.search(r'[A-Z]', password):
            messages.error(request, 'Password must contain at least one uppercase letter!')
            return redirect('signup')

        if not re.search(r'[a-z]', password):
            messages.error(request, 'Password must contain at least one lowercase letter!')
            return redirect('signup')

        if not re.search(r'\d', password):
            messages.error(request, 'Password must contain at least one number!')
            return redirect('signup')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            messages.error(request, 'Password must contain at least one special character!')
            return redirect('signup')

        if User.objects.filter(username=user_name).exists():
            messages.error(request, 'Username is already taken!')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered!')
            return redirect('signup')

        try:
            user=User.objects.create_user(first_name=first_name,last_name=last_name, username=user_name,email=email,password=password)
            user.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        except:
            messages.error(request,'An error occurred. Try again ')
            
            return redirect ("signup")
        
    return render(request,'accounts/signup.html')
        

 # Forgot Password View           
@never_cache   
def forgot_password(request):
   
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            messages.error(request, 'Email is required!')
            return redirect('forgot_password')

        user = User.objects.filter(email=email).first()
        if user:
            otp = random.randint(100000, 999999)
            cache.set(f'otp_{email}', otp, timeout=300)  # Cache OTP for 5 minutes
            send_mail(
                'Password Reset OTP',
                f'Your OTP is {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            messages.success(request, 'OTP sent to your email. Please check your inbox.')
            return redirect(reverse('verify_otp') + f'?email={email}')
        else:
            messages.error(request, 'Email not found!')

    return render(request, 'accounts/forgot_password.html')


# Verify OTP View
@never_cache
def verify_otp(request):
   
    email = request.GET.get('email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        otp = request.POST.get('otp')
        cached_otp = cache.get(f'otp_{email}')

        if cached_otp and str(cached_otp) == otp:
            cache.delete(f'otp_{email}')  # Clear OTP after use
            return redirect(reverse('reset_password') + f'?email={email}')
        else:
            messages.error(request, 'Invalid OTP or OTP expired!')
            return redirect(reverse('verify_otp') + f'?email={email}')

    return render(request, 'accounts/verify_otp.html', {'email': email})


# Reset Password View
@never_cache
def reset_password(request):
    
    email = request.GET.get('email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect(reverse('reset_password') + f'?email={email}')
        
        if not password or not confirm_password:
            messages.error(request, 'All fields are required.')
            return redirect(reverse('reset_password') + f'?email={email}')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long!')
            return redirect(reverse('reset_password') + f'?email={email}')
            
        
        if not re.search(r'[A-Z]', password):
            messages.error(request, 'Password must contain at least one uppercase letter!')
            return redirect(reverse('reset_password') + f'?email={email}')

        if not re.search(r'[a-z]', password):
            messages.error(request, 'Password must contain at least one lowercase letter!')
            return redirect(reverse('reset_password') + f'?email={email}')

        if not re.search(r'\d', password):
            messages.error(request, 'Password must contain at least one number!')
            return redirect(reverse('reset_password') + f'?email={email}')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            messages.error(request, 'Password must contain at least one special character!')
            return redirect(reverse('reset_password') + f'?email={email}')
        
        user = User.objects.filter(email=email).first()
        if user:
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'An error occurred! Please try again later.')

    return render(request, 'accounts/reset_password.html', {'email': email})


@login_required
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    messages.success(request,'You have been logged out')
    return redirect('login')

@login_required
def admin_home(request):
    if request.user.is_superuser:
        return render(request,'index.html')
    return redirect('login')

@login_required
def main_page(request):
    if not request.user.is_superuser:
        return render(request,'main.html')
    return redirect('login')


