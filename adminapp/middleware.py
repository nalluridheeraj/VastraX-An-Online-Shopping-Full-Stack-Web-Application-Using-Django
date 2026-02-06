from django.shortcuts import redirect
from django.contrib import messages


class AdminAccessMiddleware:
    """Block regular users from accessing adminapp URLs. Only session with admin_logged_in can access."""
    ADMIN_PREFIX = '/adminapp/'
    EXEMPT_PATHS = ['/adminapp/login/', '/adminapp/otp-send/', '/adminapp/otp-verify/']  # login pages

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path.startswith(self.ADMIN_PREFIX):
            is_exempt = any(path.startswith(p) or path == p.rstrip('/') for p in self.EXEMPT_PATHS)
            if not is_exempt and not request.session.get('admin_logged_in'):
                messages.warning(request, 'Access denied. Please login as Admin.')
                return redirect('mainapp:home')
        return self.get_response(request)
