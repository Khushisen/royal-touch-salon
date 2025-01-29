from django.shortcuts import render,redirect,get_object_or_404
from .models import Product,Cart,Order
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail


razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def signup(request):
    if request.method=='POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request,'Passwords do not match!')
            return render(request,'signup.html')
        
        if User.objects.filter(username = username).exists():
            messages.error(request,'Username already exists!')
            return render(request,'signup.html')
        
        user = User.objects.create_user(username = username,password = password1)
        user.save()
        
        login(request,user)
        messages.success(request,'Signup successful! You are now logged in.')
        return redirect('products')
    else:
        return render(request,'signup.html')

def user_login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('products')
    return render(request,'login.html')

def user_logout(request):
    logout(request)
    return redirect('products')

def product_list(request):
    products = Product.objects.all()
    return render(request,'products.html',{'products':products})

@login_required
def add_to_cart(request,product_id):
    if not request.user.is_authenticated:
        messages.error(request,'You need to login to add items to the cart.')
        return redirect('login')
    
    product = get_object_or_404(Product, id = product_id)
    cart_item,created = Cart.objects.get_or_create(user = request.user,product=product)
    if created:
        messages.success(request,f'{product.product_name} has been added to your cart.')
    else:
        cart_item.quantity +=1
        cart_item.save()
        messages.info(request,f'Quantity of {product.product_name} has been updated.')
    return redirect('view_cart')

@login_required
def view_cart(request):
    if not request.user.is_authenticated:
        messages.error(request,'You need to login to view your cart.')
        return redirect('login')
    
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum(item.total_price() for item in cart_items)
    return render(request,'view_cart.html',{'cart_items' : cart_items, 'total_amount':total_amount})

def remove_from_cart(request,cart_item_id):
    if not request.user.is_authenticated:
        messages.error(request,'You need to log in to manage your cart.')
        return redirect('login')
    cart_item = get_object_or_404(Cart, id=cart_item_id,user=request.user)
    cart_item.delete()
    messages.success(request,f'{cart_item.product.product_name} has been removed from your cart.')
    return redirect('view_cart')


@login_required
def order_confirmation(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum(item.total_price() for item in cart_items)
    
    if total_amount<=0:
        messages.error(request,"Your cart is empty.Please add items before proceeding.")
    
    razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
    razorpay_order = razorpay_client.order.create(
        {
            "amount" : int(total_amount*100),
            "currency":"INR",
            "payment_capture":'0'
            })
    
    razorpay_order_id = razorpay_order['id']
    
    if request.method == 'POST':
        address = request.POST.get('address')
        for item in cart_items:
            Order.objects.create(user=request.user,product=item.product,address=address)
        cart_items.delete()
        
        admin_mail = 'khushisen9001@gmail.com'
        subject = "New Order Placed"
        message = f"Customer {request.user.username} has placed an order with total amount: Rs{total_amount}.\nDelivery Address: {address}."
        send_mail(subject,message,settings.EMAIL_HOST_USER, [admin_email])
        
        return redirect('order_success')
    
    callback_url = '/products/order_success/'
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': int(total_amount * 100),  # Pass amount in paise
        'currency': "INR",
        'callback_url': callback_url,
        
    }
    
    return render(request,'order_confirmation.html',context=context)

@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            # Razorpay payment details
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            if not (payment_id and razorpay_order_id and signature):
                return HttpResponseBadRequest("Invalid payment details.")

            # Verify payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Capture the payment
            cart_items = Cart.objects.filter(user=request.user)
            total_amount = sum(item.total_price() for item in cart_items)
            amount = int(total_amount * 100)

            razorpay_client.payment.capture(payment_id, amount)
            return redirect('order_success')
        except razorpay.errors.SignatureVerificationError as e:
            return render(request, 'paymentfail.html', {'error': "Signature verification failed!"})
        except Exception as e:
            return render(request, 'paymentfail.html', {'error': str(e)})
    else:
        return HttpResponseBadRequest("Invalid request method.")


@csrf_exempt
def order_success(request):
    return render(request, 'order_success.html')