from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mainapp.urls', namespace='mainapp')),
    path('user/', include('userapp.urls', namespace='userapp')),
    path('adminapp/', include('adminapp.urls', namespace='adminapp')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
