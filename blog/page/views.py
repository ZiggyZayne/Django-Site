from django.shortcuts import render, redirect
from .models import *
from django.views import generic
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm 
from .forms import CreateUserForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import datetime
import json
from .utils import cookieCart, cartData, guestOrder
from django.contrib import messages
import mimetypes
import os
from django.http.response import HttpResponse
# Create your views here.

def blog_post(request, slug):
    post = Post.objects.get(slug=slug)
    slug_field = 'slug'
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()
    context={'products':products, 'cartItems' :cartItems, 'post' :post, 'slug_field':slug_field}
    return render(request, 'C:/Users/Zayne/AppData/Roaming/Python/Python39/blog/page/Templates/Blog/blog_post.html', context)

def blogPage(request):
    post = Post.objects.filter(status=1).order_by('-created_on')
    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()
    context={'products' :products, 'cartItems' :cartItems, 'post' :post}
    return render(request, 'C:/Users/Zayne/AppData/Roaming/Python/Python39/blog/page/Templates/Blog/blog_page.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login_page')

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('Blog')
        else: 
            message = "Login Failed!"

    context = {}
    return render(request, 'C:/Users/Zayne/AppData/Roaming/Python/Python39/blog/page/Templates/Blog/login.html', context) 

def registerPage(request):
    form = CreateUserForm()
    if request.method == "POST":
        name = request.POST.get('username')
        email = request.POST.get('email')
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            Customer.objects.create(
                user=user,
                name=name,
                email=email
            )
            #messages.success(request, 'Account was created for' + customer)
            return redirect('login_page')
    context = {'form':form}
    return render(request, 'C:/Users/Zayne/AppData/Roaming/Python/Python39/blog/page/Templates/Blog/register.html', context)

def Blog(request):

    data = cartData(request)
    cartItems = data['cartItems']
    products = Product.objects.all()
    context={'products' :products, 'cartItems' :cartItems}
    return render(request, 'C:/Users/Zayne/AppData/Roaming/Python/Python39/blog/page/Templates/Blog/Blog.html', context)

def cart(request):

    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context={'items' :items, 'order' :order, 'cartItems' :cartItems}
    return render(request, 'C:/Users/Zayne/AppData/Roaming/Python/Python39/blog/page/Templates/Blog/cart.html', context)

def download_file(request):
    fl_path = 'C:/users/zayne/appdata/roaming/python/python39/scripts/blog/static/files'
    filename = ''
    fl = open(fl_path, 'r')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context={'items' :items, 'order' :order, 'cartItems' :cartItems}
    return render(request, 'C:/Users/Zayne/AppData/Roaming/Python/Python39/blog/page/Templates/Blog/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action: ', action)
    print('productId: ', productId)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()


    return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.object.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            )

    return JsonResponse('Payment submitted', safe=False)