from django.urls import path
from . import views

app_name = 'mainapp'
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('collections/', views.collections, name='collections'),
    path('collections/mens/', views.collection_mens, name='collection_mens'),
    path('collections/womens/', views.collection_womens, name='collection_womens'),
    path('collections/kids/', views.collection_kids, name='collection_kids'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
]
