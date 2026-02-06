from userapp.models import Cart, CartItem


def cart_count(request):
    count = 0
    if request.session.get('user_id'):
        cart = Cart.objects.filter(user_id=request.session['user_id']).first()
        if cart:
            count = cart.total_items
    elif request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()
        if cart:
            count = cart.total_items
    return {'cart_count': count}
