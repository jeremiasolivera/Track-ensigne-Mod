
from django.contrib import admin
from django.urls import path, include
from myapp import urls
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Home, name='home'),
    path('app/', include(urls)),
    path('accounts/', include('allauth.urls')),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
