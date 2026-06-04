from django.urls import path
from . import views

urlpatterns = [
    path('', views.contacts, name='contacts'),
    path('feedback/', views.contacts, name='feedback'),
]