# accounts/urls.py - минимальная версия
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Регистрация и авторизация
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='catalog:catalog'), name='logout'),
    
    # Профиль пользователя
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Избранное (минимальный набор)
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('favorites/toggle/<int:kitchen_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/remove/<int:favorite_id>/', views.remove_favorite, name='remove_favorite'),
]