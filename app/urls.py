from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name='add_cart'),
    path('update-cart/<int:cart_id>/', views.update_cart, name='update_cart'),
    path('delete-cart/<int:cart_id>/', views.remove_cart, name='remove_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/create-checkout-session/', views.payment_view, name='stripe_payment'),
    path('payment_fail/', views.payment_cancel_view, name='payment_cancel'),
    path('order-history/', views.order, name='order-history'),

    path('like-product/<slug:slug>/', views.like_product, name='like'),
]