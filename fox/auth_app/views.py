
from django.shortcuts import render,redirect
from . models import *
from admin_app.models import Offer
from user_app.models import UserProfile
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.urls import reverse
from django.conf import settings
import random
import re


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, 'Both username and password are required!')
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Get the last login time and other necessary session values
                last_login = user.last_login
                otp_verified = request.session.get('otp_verified', False)
                now = timezone.now()

                # Check if OTP is required (first-time login or after long inactivity or another user logged in)
                otp_needed = False

                # Condition 1: If first-time login (last_login is None)
                if last_login is None:
                    otp_needed = True

                # Condition 2: If last login was more than 30 days ago, OTP is required
                if last_login and now - last_login > timedelta(days=30):
                    otp_needed = True

                # Condition 3: If the user logged in after another user (session management)
                if (request.session.get('last_user') and request.session['last_user'] != user.username):
                    otp_needed = True

                if otp_needed and not otp_verified:
                    # Trigger OTP flow if OTP is needed
                    otp = random.randint(100000, 999999)
                    cache.set(f'otp_{user.email}', otp, timeout=300)  # Cache OTP for 5 minutes
                    send_mail(
                        'Login OTP Verification',
                        f'Your OTP is {otp}',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                    )
                    request.session['otp_pending_user'] = user.id  # Save user for OTP
                    return redirect('verify_otp_login')  # Redirect to OTP verification page
                
                # Normal login flow if OTP is not needed
                auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # Specify backend here
                request.session['username'] = user.username
                request.session['last_user'] = user.username
                request.session['otp_verified'] = False  # Reset OTP session flag
                messages.success(request, f"Welcome {user.username}!")
                
                if user.is_superuser:
                    return redirect('admin_home')
                else:
                    return redirect('main')
            else:
                messages.error(request, 'Your account has been blocked. Please contact support.')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')

    return render(request, 'accounts/login.html')


@never_cache
def verify_otp_login(request):
    user_id = request.session.get('otp_pending_user')
    if not user_id:
        return redirect('login')

    user = User.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, 'User not found!')
        return redirect('login')

    if request.method == 'POST':
        otp = request.POST.get('otp')
        cached_otp = cache.get(f'otp_{user.email}')

        if cached_otp and str(cached_otp) == otp:
            cache.delete(f'otp_{user.email}')  # Clear OTP after use
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # Specify backend here
            request.session['otp_verified'] = True
            request.session['last_user'] = user.username
            messages.success(request, 'OTP verified successfully! Welcome.')
            
            if user.is_superuser:
                return redirect('admin_home')
            else:
                return redirect('main')
        else:
            messages.error(request, 'Invalid OTP or OTP expired!')

    return render(request, 'accounts/verify_otp_login.html', {'email': user.email})

@never_cache
def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_name = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        referral_code = request.POST.get('referral_code')  # Get referral code from form

        # Validation checks
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

        # Check if referral code exists and is valid
        offer = None
        if referral_code:
            print(f"Referral Code Submitted: {referral_code}")  # Debugging
            offer = Offer.objects.filter(referral_code__iexact=referral_code).first()
            if not offer:
                print("Referral code does not match any offer.")  # Debugging
                messages.error(request, 'Invalid referral code!')
                return redirect('signup')

        try:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=user_name,
                email=email,
                password=password
            )
            user.save()

            # If valid referral code, link offer to user profile (if applicable)
            if offer:
                user_profile = UserProfile.objects.create(user=user, referral_offer=offer)
                user_profile.save()

            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('signup')

    return render(request, 'accounts/signup.html')


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


