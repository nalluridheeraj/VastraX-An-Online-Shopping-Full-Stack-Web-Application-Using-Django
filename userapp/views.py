import random
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from mainapp.models import Product, Coupon, Offer
from .models import User, Cart, CartItem, Address, Order, OrderItem


def _generate_otp():
    return ''.join(str(random.randint(0, 9)) for _ in range(6))


def _get_or_create_cart(request):
    if request.session.get('user_id'):
        cart, _ = Cart.objects.get_or_create(user_id=request.session['user_id'], defaults={})
        return cart
    if not request.session.session_key:
        request.session.create()
    cart = Cart.objects.filter(session_key=request.session.session_key).first()
    if not cart:
        cart = Cart.objects.create(session_key=request.session.session_key)
    return cart


def login_page(request):
    return render(request, 'userapp/login.html', {'page': 'login'})


def register_page(request):
    return render(request, 'userapp/register.html', {'page': 'register'})


def register_submit(request):
    if request.method != 'POST':
        return redirect('userapp:register')
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    if not name or not email or not password:
        messages.error(request, 'Name, email and password are required.')
        return redirect('userapp:register')
    if User.objects.filter(email=email).exists():
        messages.error(request, 'An account with this email already exists.')
        return redirect('userapp:register')
    user = User.objects.create(name=name, email=email, password=password)
    subject = 'Welcome to VastraX – Your Fashion Journey Begins!'
    body_plain = f"""Hey {name}, Thank you for registering on VastraX. Enjoy our wide range of collections from all categories. Team VastraX"""
    html_message = f"""
    <div style="font-family: sans-serif; max-width: 560px; margin: 0 auto; padding: 24px;">
      <h1 style="color: #1a365d; margin-bottom: 16px;">Hey {name}! 👋</h1>
      <p style="font-size: 18px; line-height: 1.6; color: #2d3748;">Thank you for registering on <strong>VastraX</strong>.</p>
      <p style="font-size: 16px; line-height: 1.6; color: #4a5568;">Enjoy our wide range of collections from all categories — ethnic wear, western, casual & formal for <strong>Men</strong>, <strong>Women</strong> & <strong>Kids</strong>.</p>
      <p style="font-size: 16px; line-height: 1.6;">We're excited to have you. Start exploring and get your favourites delivered to your doorstep.</p>
      <p style="margin-top: 24px; font-size: 16px; color: #1a365d;"><strong>Happy Shopping!</strong><br/>— Team VastraX</p>
    </div>
    """
    try:
        send_mail(
            subject=subject,
            message=body_plain,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
            html_message=html_message,
        )
    except Exception:
        pass
    messages.success(request, 'Registration successful! Please login.')
    return redirect('userapp:login')


def otp_send(request):
    if request.method != 'POST':
        return redirect('userapp:login')
    email = request.POST.get('email', '').strip()
    login_as = request.POST.get('login_as', 'user')  # 'user' or 'admin'
    if not email:
        messages.error(request, 'Email is required.')
        return redirect('userapp:login')
    if login_as == 'admin':
        from adminapp.models import AdminUser
        admin_user = AdminUser.objects.filter(email=email).first()
        if not admin_user:
            messages.warning(request, 'Invalid Credentials. No admin account found for this email.')
            return redirect('userapp:login')
        otp = _generate_otp()
        admin_user.otp = otp
        admin_user.save()
        try:
            send_mail(
                subject='Your VastraX Admin OTP',
                message=f'Your one-time password for admin login is: {otp}. Valid for 10 minutes.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            messages.error(request, 'Could not send OTP. Please try again.')
            return redirect('userapp:login')
        request.session['otp_email'] = email
        request.session['otp_login_as'] = 'admin'
        return redirect('userapp:otp_verify_page')
    else:
        user = User.objects.filter(email=email).first()
        if not user:
            messages.warning(request, 'Invalid Credentials. No account found for this email. Please register.')
            return redirect('userapp:login')
        otp = _generate_otp()
        user.otp = otp
        user.save()
        try:
            send_mail(
                subject='Your VastraX Login OTP',
                message=f'Hi {user.name}, your one-time password is: {otp}. Valid for 10 minutes.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            messages.error(request, 'Could not send OTP. Please try again.')
            return redirect('userapp:login')
        request.session['otp_email'] = email
        request.session['otp_login_as'] = 'user'
        return redirect('userapp:otp_verify_page')


def otp_verify_page(request):
    email = request.session.get('otp_email')
    if not email:
        return redirect('userapp:login')
    return render(request, 'userapp/verify_otp.html', {'email': email, 'page': 'login'})


def otp_verify(request):
    if request.method != 'POST':
        return redirect('userapp:login')
    email = request.session.get('otp_email')
    login_as = request.session.get('otp_login_as', 'user')
    otp_entered = request.POST.get('otp', '').strip()
    if not email or not otp_entered:
        messages.error(request, 'Invalid request.')
        return redirect('userapp:login')
    if login_as == 'admin':
        from adminapp.models import AdminUser
        admin_user = AdminUser.objects.filter(email=email).first()
        if not admin_user or admin_user.otp != otp_entered:
            messages.warning(request, 'Invalid Credentials. Wrong OTP or session expired.')
            if admin_user:
                admin_user.otp = ''
                admin_user.save()
            request.session.pop('otp_email', None)
            request.session.pop('otp_login_as', None)
            return redirect('userapp:login')
        admin_user.otp = ''
        admin_user.save()
        request.session['admin_logged_in'] = True
        request.session['admin_id'] = admin_user.id
        request.session.pop('otp_email', None)
        request.session.pop('otp_login_as', None)
        messages.success(request, 'Welcome back, Admin!')
        return redirect('adminapp:dashboard')
    else:
        user = User.objects.filter(email=email).first()
        if not user or user.otp != otp_entered:
            messages.warning(request, 'Invalid Credentials. Wrong OTP or session expired.')
            if user:
                user.otp = ''
                user.save()
            request.session.pop('otp_email', None)
            request.session.pop('otp_login_as', None)
            return redirect('userapp:login')
        user.otp = ''
        user.save()
        request.session['user_id'] = user.id
        request.session['user_name'] = user.name
        request.session.pop('otp_email', None)
        request.session.pop('otp_login_as', None)
        messages.success(request, f'Welcome, {user.name}!')
        return redirect('mainapp:home')


def logout_view(request):
    if request.session.get('admin_logged_in'):
        request.session.flush()
        messages.info(request, 'You have been logged out.')
        return redirect('mainapp:home')
    request.session.pop('user_id', None)
    request.session.pop('user_name', None)
    request.session.pop('coupon_code', None)
    request.session.pop('coupon_discount', None)
    messages.info(request, 'You have been logged out.')
    return redirect('mainapp:home')


def dashboard(request):
    if not request.session.get('user_id'):
        messages.warning(request, 'Please login to view dashboard.')
        return redirect('userapp:login')
    user = get_object_or_404(User, pk=request.session['user_id'])
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    return render(request, 'userapp/dashboard.html', {'user': user, 'recent_orders': recent_orders, 'page': 'dashboard'})


def cart(request):
    cart_obj = _get_or_create_cart(request)
    items = CartItem.objects.filter(cart=cart_obj).select_related('product')
    subtotal = sum((item.product.price * item.quantity) for item in items)
    return render(request, 'userapp/cart.html', {'cart': cart_obj, 'items': items, 'subtotal': subtotal, 'page': 'cart'})


def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if product.stock < 1:
        messages.warning(request, 'Product is out of stock.')
        return redirect(request.META.get('HTTP_REFERER', 'mainapp:home'))
    cart_obj = _get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart_obj, product=product, defaults={'quantity': 1})
    if not created:
        if item.quantity >= product.stock:
            messages.warning(request, 'Maximum available quantity added.')
        else:
            item.quantity += 1
            item.save()
    else:
        messages.success(request, f'{product.name} added to cart.')
    return redirect(request.META.get('HTTP_REFERER', 'userapp:cart'))


def cart_update(request, item_id):
    cart_obj = _get_or_create_cart(request)
    item = CartItem.objects.filter(cart=cart_obj, id=item_id).first()
    if not item:
        return redirect('userapp:cart')
    qty = request.POST.get('quantity')
    try:
        qty = max(1, min(int(qty), item.product.stock))
    except (TypeError, ValueError):
        qty = item.quantity
    item.quantity = qty
    item.save()
    messages.success(request, 'Cart updated.')
    return redirect('userapp:cart')


def cart_remove(request, item_id):
    cart_obj = _get_or_create_cart(request)
    CartItem.objects.filter(cart=cart_obj, id=item_id).delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('userapp:cart')


def addresses(request):
    if not request.session.get('user_id'):
        return redirect('userapp:login')
    user = get_object_or_404(User, pk=request.session['user_id'])
    addrs = Address.objects.filter(user=user)
    return render(request, 'userapp/addresses.html', {'addresses': addrs, 'page': 'addresses'})


def address_add(request):
    if not request.session.get('user_id') or request.method != 'POST':
        return redirect('userapp:addresses')
    user = get_object_or_404(User, pk=request.session['user_id'])
    is_default = not Address.objects.filter(user=user).exists()
    Address.objects.create(
        user=user,
        full_name=request.POST.get('full_name'),
        phone=request.POST.get('phone'),
        address_line1=request.POST.get('address_line1'),
        address_line2=request.POST.get('address_line2', ''),
        city=request.POST.get('city'),
        state=request.POST.get('state'),
        pincode=request.POST.get('pincode'),
        is_default=is_default,
    )
    messages.success(request, 'Address added.')
    return redirect('userapp:addresses')


def address_edit(request, pk):
    if not request.session.get('user_id'):
        return redirect('userapp:login')
    addr = get_object_or_404(Address, pk=pk, user_id=request.session['user_id'])
    if request.method == 'POST':
        addr.full_name = request.POST.get('full_name', addr.full_name)
        addr.phone = request.POST.get('phone', addr.phone)
        addr.address_line1 = request.POST.get('address_line1', addr.address_line1)
        addr.address_line2 = request.POST.get('address_line2', '')
        addr.city = request.POST.get('city', addr.city)
        addr.state = request.POST.get('state', addr.state)
        addr.pincode = request.POST.get('pincode', addr.pincode)
        if request.POST.get('is_default') == 'on':
            Address.objects.filter(user=addr.user).update(is_default=False)
            addr.is_default = True
        addr.save()
        messages.success(request, 'Address updated.')
        return redirect('userapp:addresses')
    return render(request, 'userapp/address_edit.html', {'address': addr})


def address_delete(request, pk):
    if not request.session.get('user_id'):
        return redirect('userapp:login')
    addr = get_object_or_404(Address, pk=pk, user_id=request.session['user_id'])
    addr.delete()
    messages.success(request, 'Address removed.')
    return redirect('userapp:addresses')


def apply_coupon(request):
    if request.method != 'POST':
        return redirect('userapp:checkout')
    code = request.POST.get('coupon_code', '').strip()
    request.session.pop('coupon_code', None)
    request.session.pop('coupon_discount', None)
    if not code:
        messages.info(request, 'Coupon removed.')
        return redirect('userapp:checkout')
    coupon = Coupon.objects.filter(code__iexact=code, is_active=True).first()
    if not coupon:
        messages.error(request, 'Invalid or expired coupon.')
        return redirect('userapp:checkout')
    from django.utils import timezone
    now = timezone.now()
    if coupon.valid_from and now < coupon.valid_from:
        messages.error(request, 'Coupon not yet valid.')
        return redirect('userapp:checkout')
    if coupon.valid_to and now > coupon.valid_to:
        messages.error(request, 'Coupon has expired.')
        return redirect('userapp:checkout')
    if coupon.max_uses and coupon.used_count >= coupon.max_uses:
        messages.error(request, 'Coupon usage limit reached.')
        return redirect('userapp:checkout')
    cart_obj = _get_or_create_cart(request)
    items = CartItem.objects.filter(cart=cart_obj)
    subtotal = sum((item.product.price * item.quantity) for item in items)
    if subtotal < coupon.min_order_value:
        messages.error(request, f'Minimum order value for this coupon is ₹{coupon.min_order_value}.')
        return redirect('userapp:checkout')
    if coupon.discount_type == 'percent':
        discount = (subtotal * coupon.discount_value / 100).quantize(Decimal('0.01'))
    else:
        discount = min(coupon.discount_value, subtotal)
    request.session['coupon_code'] = coupon.code
    request.session['coupon_discount'] = str(discount)
    request.session['coupon_id'] = coupon.id
    messages.success(request, f'Coupon applied! You save ₹{discount}.')
    return redirect('userapp:checkout')


def checkout(request):
    cart_obj = _get_or_create_cart(request)
    items = CartItem.objects.filter(cart=cart_obj).select_related('product')
    if not items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('mainapp:home')
    subtotal = sum((item.product.price * item.quantity) for item in items)
    discount = Decimal(request.session.get('coupon_discount', 0))
    total = max(Decimal('0'), subtotal - discount)
    user = None
    addresses_list = []
    if request.session.get('user_id'):
        user = User.objects.filter(pk=request.session['user_id']).first()
        addresses_list = Address.objects.filter(user=user)
    return render(request, 'userapp/checkout.html', {
        'items': items, 'subtotal': subtotal, 'discount': discount, 'total': total,
        'user': user, 'addresses': addresses_list, 'page': 'checkout',
    })


def _create_order(request, user, address, cart_obj, subtotal, discount, total, coupon_id=None):
    import uuid
    order_number = 'VX' + str(uuid.uuid4().hex[:10].upper())
    order = Order.objects.create(
        user=user,
        order_number=order_number,
        address=address,
        coupon_id=coupon_id,
        subtotal=subtotal,
        discount=discount,
        total=total,
        payment_status='paid',  # Simulated payment success
    )
    for item in CartItem.objects.filter(cart=cart_obj):
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
            total=item.product.price * item.quantity,
        )
        item.product.stock -= item.quantity
        item.product.save()
    if coupon_id:
        c = Coupon.objects.filter(pk=coupon_id).first()
        if c:
            c.used_count += 1
            c.save()
    CartItem.objects.filter(cart=cart_obj).delete()
    request.session.pop('coupon_code', None)
    request.session.pop('coupon_discount', None)
    request.session.pop('coupon_id', None)
    return order


def orders(request):
    if not request.session.get('user_id'):
        return redirect('userapp:login')
    user = get_object_or_404(User, pk=request.session['user_id'])
    order_list = (
        Order.objects
        .filter(user=user)
        .order_by('-created_at')
        .prefetch_related('orderitem_set__product')
    )
    return render(request, 'userapp/orders.html', {'orders': order_list, 'page': 'orders'})


def order_detail(request, order_number):
    if not request.session.get('user_id'):
        return redirect('userapp:login')
    order = get_object_or_404(Order, order_number=order_number, user_id=request.session['user_id'])
    items = OrderItem.objects.filter(order=order).select_related('product')
    return render(request, 'userapp/order_detail.html', {'order': order, 'items': items})


# Place order (form in checkout submits here)
def place_order(request):
    if request.method != 'POST':
        return redirect('userapp:checkout')
    cart_obj = _get_or_create_cart(request)
    items = list(CartItem.objects.filter(cart=cart_obj).select_related('product'))
    if not items:
        messages.warning(request, 'Cart is empty.')
        return redirect('userapp:cart')
    user_id = request.session.get('user_id')
    if not user_id:
        messages.warning(request, 'Please login to place order.')
        return redirect('userapp:login')
    user = get_object_or_404(User, pk=user_id)
    address_id = request.POST.get('address')
    if not address_id:
        messages.error(request, 'Please select an address.')
        return redirect('userapp:checkout')
    address = get_object_or_404(Address, pk=address_id, user=user)
    subtotal = sum((item.product.price * item.quantity) for item in items)
    discount = Decimal(request.session.get('coupon_discount', 0))
    total = max(Decimal('0'), subtotal - discount)
    coupon_id = request.session.get('coupon_id')
    order = _create_order(request, user, address, cart_obj, subtotal, discount, total, coupon_id)
    messages.success(request, f'Order {order.order_number} placed successfully!')
    return redirect('userapp:order_detail', order_number=order.order_number)
