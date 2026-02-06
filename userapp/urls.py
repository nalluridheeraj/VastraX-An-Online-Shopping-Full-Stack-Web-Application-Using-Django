from django.urls import path
from . import views

app_name = 'userapp'
urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('register/submit/', views.register_submit, name='register_submit'),
    path('otp/send/', views.otp_send, name='otp_send'),
    path('otp/verify/', views.otp_verify, name='otp_verify'),
    path('otp/verify-page/', views.otp_verify_page, name='otp_verify_page'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('addresses/', views.addresses, name='addresses'),
    path('address/add/', views.address_add, name='address_add'),
    path('address/edit/<int:pk>/', views.address_edit, name='address_edit'),
    path('address/delete/<int:pk>/', views.address_delete, name='address_delete'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/place-order/', views.place_order, name='place_order'),
    path('checkout/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('orders/', views.orders, name='orders'),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
]
