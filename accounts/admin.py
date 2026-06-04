from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, Favorite, UserActivity


# Настройка отображения профиля пользователя в админке
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль'
    fields = ('avatar', 'phone_number', 'birth_date', 'address', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


# Расширенная админка для пользователей
# Сначала отменяем регистрацию стандартной админки User (если она зарегистрирована)
try:
    admin.site.unregister(User)
except Exception:
    # Если User еще не зарегистрирован, игнорируем ошибку
    pass

# Теперь регистрируем нашу кастомную админку
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined', 'is_staff', 'is_active', 'view_password_info')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    # Убираем дубликаты полей, которые уже есть в BaseUserAdmin
    pass
    
    def view_password_info(self, obj):
        """Показывает информацию о пароле (не сам пароль, т.к. он хеширован)"""
        if obj.password:
            # Показываем длину хеша и дату последнего изменения
            return format_html(
                '<span style="color: green;">✓ Пароль установлен</span><br>'
                '<small>Хеш: {} символов</small><br>'
                '<a href="/admin/auth/user/{}/password/" style="color: blue; text-decoration: underline;">Сбросить пароль</a>',
                len(obj.password),
                obj.id
            )
        return format_html('<span style="color: red;">✗ Пароль не установлен</span>')
    
    view_password_info.short_description = 'Информация о пароле'
    
    # Добавляем возможность изменения пароля в форме редактирования
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Пароль можно изменить через стандартную форму Django
        return form


# Регистрируем кастомную админку для User
admin.site.register(User, CustomUserAdmin)


# Админка для профилей пользователей
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'birth_date', 'created_at', 'avatar_preview')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at', 'avatar_preview')
    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Личная информация', {
            'fields': ('avatar', 'avatar_preview', 'phone_number', 'birth_date', 'address')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 50%;" />',
                obj.avatar.url
            )
        return "Нет аватара"
    avatar_preview.short_description = 'Превью аватара'


# Админка для избранного
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'kitchen', 'added_at', 'priority')
    list_filter = ('added_at', 'priority')
    search_fields = ('user__username', 'kitchen__name')
    readonly_fields = ('added_at',)
    date_hierarchy = 'added_at'


# Админка для активности пользователей
@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'created_at', 'ip_address')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__username', 'activity_type')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'activity_type', 'created_at')
        }),
        ('Детали', {
            'fields': ('details', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
