from django.urls import path
from . import views

app_name = 'adminapp'
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('products/', views.products_list, name='products_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('orders/update-status/<str:order_number>/', views.order_update_status, name='order_update_status'),
    path('users/', views.users_list, name='users_list'),
    path('coupons/', views.coupons_list, name='coupons_list'),
    path('coupons/add/', views.coupon_add, name='coupon_add'),
    path('coupons/edit/<int:pk>/', views.coupon_edit, name='coupon_edit'),
    path('coupons/delete/<int:pk>/', views.coupon_delete, name='coupon_delete'),
    path('offers/', views.offers_list, name='offers_list'),
    path('offers/add/', views.offer_add, name='offer_add'),
    path('offers/edit/<int:pk>/', views.offer_edit, name='offer_edit'),
    path('offers/delete/<int:pk>/', views.offer_delete, name='offer_delete'),
]
