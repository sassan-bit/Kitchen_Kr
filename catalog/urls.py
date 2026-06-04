from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('home/', views.home, name='home'),
    path('<int:kitchen_id>/', views.kitchen_detail, name='kitchen_detail'),
]