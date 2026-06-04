from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from catalog.views import home

urlpatterns = [
    path('', home, name='home'),  # Главная страница с лентой
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('catalog/', include('catalog.urls')),  # Каталог с фильтрами
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('contacts/', include('contacts.urls')),
    path('comments/', include('comments.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)