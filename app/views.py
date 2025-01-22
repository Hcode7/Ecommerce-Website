from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import *
from django.http import JsonResponse
from .forms import *
import stripe
from django.conf import settings
from django.db.models import Sum, F

# Create your views here.


def home(request):
    product = (Product.objects.annotate(like=Sum('likes')).order_by('-like').first())
    products = Product.objects.all()[0:3]
    context = {
        'products' : products,
        'product' : product,
    }
    return render(request, 'pages/home.html', context)


def product_list(request):
    # products = Product.objects.all()
    # products = Product.objects.annotate(total_price=Sum('orderitem__quantity')).order_by('-total_price')
    
    search = request.GET.get('search', '')
    if search:
        products = Product.objects.filter(title__icontains=search)
    else:
        products = Product.objects.annotate(total_price=Sum('orderitem__quantity')).order_by('-total_price')

    form = ProductFilter(request.GET or None)
    if form.is_valid():
        products = form.filter_price(products)

    categories = request.GET.get('category')
    if categories:
        products = Product.objects.filter(categories__icontains=categories)

    
    context = {
        'products': products,
        'form' : form,
    }
    return render(request, 'pages/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    context = {
        'product' : product,
    }
    return render(request, 'pages/product_detail.html', context)

# def like_product(request, slug):
#     food = get_object_or_404(Product, slug=slug)
#     if request.user and food.likes.all():
#         food.likes.remove(request.user)
#     else:
#         food.likes.add(request.user)
#     return redirect('home')


def cart_view(request):
    if not request.session.session_key:
        request.session.create()
    if request.user.is_authenticated:
        cart  = Cart.objects.filter(user=request.user).first()
    else:
        cart  = Cart.objects.filter(session_key=request.session.session_key).first()
    
    cart_item = cart.cartitem_set.all() if cart else []

    total_price = cart_item.aggregate(
        total_price=Sum(F('product__price') * F('quantity'))
    )['total_price']
    return render(request, 'pages/cart_detail.html', {'cart' : cart, 'cart_item' : cart_item, 'total_price' : total_price})


def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if not request.session.session_key:
        request.session.create()
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)

    cartitem, created = CartItem.objects.get_or_create(product=product, cart=cart)

    if not created:
        cartitem.quantity += 1

    cartitem.save()

    return redirect('cart')


def update_cart(request, cart_id):
    if not request.session.session_key:
        request.session.create()
    if request.user.is_authenticated:
        cartitem = get_object_or_404(CartItem, id=cart_id, cart__user=request.user)
    else:
        cart = get_object_or_404(Cart, session_key=request.session.session_key)
        cartitem = get_object_or_404(CartItem, id=cart_id, cart=cart)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cartitem.quantity = quantity
        cartitem.save()
    return redirect('cart')

def remove_cart(request, cart_id):
    if not request.session.session_key:
        request.session.create()
    if request.user.is_authenticated:
        cartitem = get_object_or_404(CartItem, id=cart_id, cart__user=request.user)
    else:
        cartitem = get_object_or_404(CartItem, id=cart_id, cart__session_key=request.session.session_key)

    cartitem.delete()
    return redirect('cart')


def checkout(request):
    if not request.session.session_key:
        request.session.create()
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            shipping_address = form.save(commit=False)   
            if request.user.is_authenticated:
                order = Order.objects.create(customer=request.user)
                shipping_address.order = order
            else:
                order = Order.objects.create(session_key=request.session.session_key)
                shipping_address.order = order
            
            shipping_address.save()
            return redirect('stripe_payment')
    else:
        form = ShippingAddressForm()
    return render(request, 'pages/checkout.html', {'form' : form})
    


def payment_view(request):
    stripe.api_key = settings.STRIPE_SEC_KEY


    if not request.session.session_key:
        request.session.create()
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()

    if not cart or not cart.cartitem_set.exists():
        return redirect('cart')
    

    line_items = []
    
    cartitem = cart.cartitem_set.all()

    for item in cartitem:
        new_data = {
            'price_data' : {
                'currency' : 'usd',
                'product_data' : {
                    'name' : item.product.title,
                },
                'unit_amount' : int(item.product.price * 100),
            },
            'quantity' : item.quantity,
        }
        line_items.append(new_data)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('order-history')),
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
        )
        
        if request.user.is_authenticated:
            order = Order.objects.create(customer=request.user)
        else:
            order = Order.objects.create(session_key=request.session.session_key)

        for item in cartitem:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

    except session.error.StripeError as e:
        return render(request, 'pages.payment_error.html', {'error' : e})


    cart.cartitem_set.all().delete()
    cart.delete()

    return redirect(session.url, code=303)

def payment_cancel_view(request):
    return render(request, 'pages/payment_cancel.html')

def order(request):
    if not request.session.session_key:
        request.session.create()
        
    if request.user.is_authenticated:
        orders = Order.objects.filter(customer=request.user, is_complete=False)
    else:
        session_key = request.session.session_key
        orders = Order.objects.filter(session_key=session_key)
    
    return render(request, 'pages/order.html', {'orders' : orders})

