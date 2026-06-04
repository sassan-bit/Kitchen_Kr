from django.contrib import admin
from .models import Cart

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'kitchen', 'quantity', 'added_at')
    list_filter = ('added_at', 'user')