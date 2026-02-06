from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from mainapp.models import Product, Category, Coupon, Offer
from userapp.models import User, Order, OrderItem


def _admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_logged_in'):
            messages.warning(request, 'Access denied. Please login as Admin.')
            return redirect('userapp:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def dashboard(request):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    orders = Order.objects.all()
    total_sales = orders.aggregate(Sum('total'))['total__sum'] or 0
    total_orders = orders.count()
    orders_per_product = OrderItem.objects.values('product__name').annotate(
        total_qty=Sum('quantity'),
        order_count=Count('order', distinct=True),
    ).order_by('-total_qty')[:15]
    recent_orders = orders.order_by('-created_at')[:10]
    low_stock = Product.objects.filter(stock__lt=5).order_by('stock')[:10]
    return render(request, 'adminapp/dashboard.html', {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'orders_per_product': orders_per_product,
        'recent_orders': recent_orders,
        'low_stock': low_stock,
    })


def products_list(request):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'adminapp/products_list.html', {'products': products})


def product_add(request):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        stock = request.POST.get('stock', 0)
        gender = request.POST.get('gender', 'women')
        product_type = request.POST.get('product_type', 'other')
        category_id = request.POST.get('category') or None
        rating = request.POST.get('rating', 0)
        image = request.FILES.get('image')
        try:
            Product.objects.create(
                name=name,
                description=description,
                price=price,
                stock=int(stock),
                gender=gender,
                product_type=product_type,
                category_id=category_id,
                rating=rating,
                image=image,
            )
            messages.success(request, 'Product added.')
            return redirect('adminapp:products_list')
        except Exception as e:
            messages.error(request, str(e))
    categories = Category.objects.all()
    return render(request, 'adminapp/product_form.html', {'categories': categories, 'product': None})


def product_edit(request, pk):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name)
        product.description = request.POST.get('description', product.description)
        product.price = request.POST.get('price', product.price)
        product.stock = request.POST.get('stock', product.stock)
        product.gender = request.POST.get('gender', product.gender)
        product.product_type = request.POST.get('product_type', product.product_type)
        product.rating = request.POST.get('rating', product.rating)
        product.category_id = request.POST.get('category') or None
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product updated.')
        return redirect('adminapp:products_list')
    categories = Category.objects.all()
    return render(request, 'adminapp/product_form.html', {'product': product, 'categories': categories})


def product_delete(request, pk):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Product removed.')
    return redirect('adminapp:products_list')


def orders_list(request):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'adminapp/orders_list.html', {'orders': orders})


def order_detail(request, order_number):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    order = get_object_or_404(Order, order_number=order_number)
    items = OrderItem.objects.filter(order=order).select_related('product')
    return render(request, 'adminapp/order_detail.html', {'order': order, 'items': items})


def order_update_status(request, order_number):
    if not request.session.get('admin_logged_in') or request.method != 'POST':
        return redirect('adminapp:orders_list')
    order = get_object_or_404(Order, order_number=order_number)
    order.status = request.POST.get('status', order.status)
    order.save()
    messages.success(request, 'Order status updated.')
    return redirect('adminapp:order_detail', order_number=order_number)


def users_list(request):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    users = User.objects.all().order_by('-created_at')
    return render(request, 'adminapp/users_list.html', {'users': users})


def coupons_list(request):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    coupons = Coupon.objects.all().order_by('-created_at')
    return render(request, 'adminapp/coupons_list.html', {'coupons': coupons})


def coupon_add(request):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    if request.method == 'POST':
        code = request.POST.get('code')
        discount_type = request.POST.get('discount_type', 'percent')
        discount_value = request.POST.get('discount_value')
        min_order_value = request.POST.get('min_order_value', 0)
        max_uses = request.POST.get('max_uses') or None
        Coupon.objects.create(
            code=code,
            discount_type=discount_type,
            discount_value=discount_value,
            min_order_value=min_order_value,
            max_uses=int(max_uses) if max_uses else None,
        )
        messages.success(request, 'Coupon added.')
        return redirect('adminapp:coupons_list')
    return render(request, 'adminapp/coupon_form.html', {'coupon': None})


def coupon_edit(request, pk):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == 'POST':
        coupon.code = request.POST.get('code', coupon.code)
        coupon.discount_type = request.POST.get('discount_type', coupon.discount_type)
        coupon.discount_value = request.POST.get('discount_value', coupon.discount_value)
        coupon.min_order_value = request.POST.get('min_order_value', coupon.min_order_value)
        coupon.max_uses = request.POST.get('max_uses') or None
        if coupon.max_uses:
            coupon.max_uses = int(coupon.max_uses)
        coupon.is_active = request.POST.get('is_active') == 'on'
        coupon.save()
        messages.success(request, 'Coupon updated.')
        return redirect('adminapp:coupons_list')
    return render(request, 'adminapp/coupon_form.html', {'coupon': coupon})


def coupon_delete(request, pk):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    coupon = get_object_or_404(Coupon, pk=pk)
    coupon.delete()
    messages.success(request, 'Coupon removed.')
    return redirect('adminapp:coupons_list')


def offers_list(request):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    offers = Offer.objects.all().order_by('-created_at')
    return render(request, 'adminapp/offers_list.html', {'offers': offers})


def offer_add(request):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    if request.method == 'POST':
        title = request.POST.get('title')
        product_id = request.POST.get('product') or None
        category_id = request.POST.get('category') or None
        discount_percent = request.POST.get('discount_percent', 0)
        Offer.objects.create(
            title=title,
            product_id=product_id,
            category_id=category_id,
            discount_percent=discount_percent,
        )
        messages.success(request, 'Offer added.')
        return redirect('adminapp:offers_list')
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'adminapp/offer_form.html', {'offer': None, 'products': products, 'categories': categories})


def offer_edit(request, pk):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    offer = get_object_or_404(Offer, pk=pk)
    if request.method == 'POST':
        offer.title = request.POST.get('title', offer.title)
        offer.product_id = request.POST.get('product') or None
        offer.category_id = request.POST.get('category') or None
        offer.discount_percent = request.POST.get('discount_percent', offer.discount_percent)
        offer.is_active = request.POST.get('is_active') == 'on'
        offer.save()
        messages.success(request, 'Offer updated.')
        return redirect('adminapp:offers_list')
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'adminapp/offer_form.html', {'offer': offer, 'products': products, 'categories': categories})


def offer_delete(request, pk):
    if not request.session.get('admin_logged_in'):
        return redirect('userapp:login')
    offer = get_object_or_404(Offer, pk=pk)
    offer.delete()
    messages.success(request, 'Offer removed.')
    return redirect('adminapp:offers_list')
