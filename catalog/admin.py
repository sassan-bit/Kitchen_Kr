from django.contrib import admin
from .models import Kitchen, KitchenImage

class KitchenImageInline(admin.TabularInline):
    model = KitchenImage
    extra = 3  # Количество пустых форм для добавления новых фото
    fields = ['image', 'alt_text', 'order']
    ordering = ['order']

@admin.register(Kitchen)
class KitchenAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at', 'price']
    inlines = [KitchenImageInline]  # Добавляем галерею фото прямо на странице кухни

@admin.register(KitchenImage)
class KitchenImageAdmin(admin.ModelAdmin):
    list_display = ['kitchen', 'alt_text', 'order', 'created_at']
    list_filter = ['kitchen', 'created_at']
    search_fields = ['alt_text', 'kitchen__name']