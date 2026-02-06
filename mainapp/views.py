from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, Offer

def home(request):
    return render(request, 'mainapp/home.html', {'page': 'home'})

def about(request):
    return render(request, 'mainapp/about.html', {'page': 'about'})

def contact(request):
    return render(request, 'mainapp/contact.html', {'page': 'contact'})

def collections(request):
    products = Product.objects.filter(stock__gt=0)[:24]
    return render(request, 'mainapp/collections.html', {'products': products, 'page': 'collections'})

def collection_mens(request):
    return _collection_view(request, 'men', 'mainapp/collection_mens.html', 'collection_mens')

def collection_womens(request):
    return _collection_view(request, 'women', 'mainapp/collection_womens.html', 'collection_womens')

def collection_kids(request):
    return _collection_view(request, 'kids', 'mainapp/collection_kids.html', 'collection_kids')

def _collection_view(request, gender, template, page_name):
    products = Product.objects.filter(gender=gender, stock__gt=0)
    sort = request.GET.get('sort', '')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-created_at')
    category = request.GET.get('category', '')
    product_type = request.GET.get('type', '')
    if category:
        products = products.filter(category__slug=category)
    if product_type:
        products = products.filter(product_type=product_type)
    categories = Category.objects.all()
    return render(request, template, {
        'products': products,
        'categories': categories,
        'page': page_name,
        'current_sort': sort,
        'current_category': category,
        'current_type': product_type,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    offers = Offer.objects.filter(product=product, is_active=True) | Offer.objects.filter(category=product.category, is_active=True)
    return render(request, 'mainapp/product_detail.html', {'product': product, 'offers': offers[:5]})
