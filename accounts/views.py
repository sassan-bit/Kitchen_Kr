# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
import json

from .models import UserProfile, Favorite
from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm
from catalog.models import Kitchen

# ============= АВТОРИЗАЦИЯ =============

def register(request):
    """Простая и надежная регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Сохраняем пользователя с проверками
                user = form.save(commit=True)
                
                # Проверяем, что пользователь действительно сохранен
                if user is None:
                    raise ValueError("Не удалось создать пользователя")
                
                if not hasattr(user, 'pk') or user.pk is None:
                    raise ValueError("Пользователь не был сохранен в базу данных")
                
                # Создаем профиль вручную (без сигналов) с задержкой
                from django.db import transaction
                try:
                    # Используем транзакцию для безопасности
                    with transaction.atomic():
                        profile, created = UserProfile.objects.get_or_create(user=user)
                        if created:
                            print(f"Профиль создан для пользователя {user.username}")
                except Exception as e:
                    import traceback
                    print(f"Ошибка создания профиля: {e}")
                    traceback.print_exc()
                    # Не критично, профиль можно создать позже
                
                # Автоматический вход после регистрации
                try:
                    login(request, user)
                    messages.success(request, f'Добро пожаловать, {user.username}! Регистрация прошла успешно.')
                    return redirect('profile')
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    messages.error(request, f'Ошибка при входе: {str(e)}')
                    return render(request, 'accounts/register.html', {'form': form})
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                messages.error(request, f'Ошибка при регистрации: {str(e)}')
                return render(request, 'accounts/register.html', {'form': form})
        else:
            # Показываем ошибки формы
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def custom_login(request):
    """Вход в систему"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Создаем профиль, если его нет
            try:
                user.profile
            except UserProfile.DoesNotExist:
                UserProfile.objects.get_or_create(user=user)
            
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('profile')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


# ============= ПРОФИЛЬ =============

@login_required
def profile(request):
    """Страница профиля пользователя"""
    user = request.user
    
    # Получаем или создаем профиль
    try:
        profile_obj = user.profile
    except UserProfile.DoesNotExist:
        profile_obj = UserProfile.objects.create(user=user)
    
    # Получаем избранное
    favorites = user.favorites.select_related('kitchen').all()[:12]
    
    # Пытаемся получить заказы (если приложение orders существует)
    orders = []
    try:
        from orders.models import Order
        orders = Order.objects.filter(user=user).prefetch_related('orderitem_set__kitchen').order_by('-created_at')[:5]
    except:
        pass
    
    context = {
        'user': user,
        'profile': profile_obj,
        'avatar_url': profile_obj.get_avatar_url(),
        'favorites': favorites,
        'orders': orders,
        'stats': {
            'total_orders': len(orders),
            'total_favorites': user.favorites.count(),
        }
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit(request):
    """Редактирование профиля"""
    user = request.user
    
    try:
        profile_instance = user.profile
    except UserProfile.DoesNotExist:
        profile_instance = UserProfile.objects.create(user=user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile_instance)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile_instance)
    
    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


# ============= ИЗБРАННОЕ =============

@login_required
def favorite_list(request):
    """Список избранных товаров"""
    favorites = request.user.favorites.select_related('kitchen').all()
    return render(request, 'accounts/favorite_list.html', {
        'favorites': favorites,
        'title': 'Избранные товары'
    })


@login_required
@require_POST
def toggle_favorite(request, kitchen_id):
    """Добавляет или удаляет товар из избранного."""
    try:
        kitchen = Kitchen.objects.get(id=kitchen_id)
    except Kitchen.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Товар не найден'}, status=404)
        messages.error(request, 'Товар не найден')
        return redirect('catalog')
    
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        kitchen=kitchen
    )
    
    if not created:
        # Удаляем, если уже был в избранном
        favorite.delete()
        is_favorite = False
        action = 'removed'
        message = f'Товар "{kitchen.name}" удален из избранного'
    else:
        # Добавили в избранное
        is_favorite = True
        action = 'added'
        message = f'Товар "{kitchen.name}" добавлен в избранное'
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite,
            'action': action,
            'kitchen_id': kitchen_id,
            'kitchen_name': kitchen.name,
            'total_favorites': request.user.favorites.count(),
            'message': message
        })
    
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'catalog'))


@login_required
@require_POST
def remove_favorite(request, favorite_id):
    """Удаляет товар из избранного."""
    favorite = get_object_or_404(Favorite, id=favorite_id, user=request.user)
    kitchen_name = favorite.kitchen.name
    favorite.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'Товар "{kitchen_name}" удален из избранного',
            'total_favorites': request.user.favorites.count()
        })
    
    messages.success(request, f'Товар "{kitchen_name}" удален из избранного')
    return redirect('favorite_list')


@login_required
@require_POST
def update_favorite_note(request, favorite_id):
    """Обновляет заметку для избранного товара."""
    try:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = json.loads(request.body)
            note = data.get('note', '').strip()
            
            favorite = Favorite.objects.get(id=favorite_id, user=request.user)
            favorite.note = note
            favorite.save()
            
            return JsonResponse({
                'status': 'success',
                'note': note
            })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ============= API ENDPOINTS =============

@login_required
def check_favorite_status(request, kitchen_id):
    """Проверяет, добавлен ли товар в избранное (для AJAX)."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        is_favorite = Favorite.objects.filter(
            user=request.user,
            kitchen_id=kitchen_id
        ).exists()
        
        return JsonResponse({
            'is_favorite': is_favorite,
            'kitchen_id': kitchen_id
        })
    
    return HttpResponseForbidden()


@login_required
def get_favorites_count(request):
    """Возвращает количество избранных товаров (для AJAX)."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        count = request.user.favorites.count()
        return JsonResponse({'count': count})
    
    return HttpResponseForbidden()


@login_required
def user_stats(request):
    """Статистика пользователя (для AJAX)."""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        import datetime
        from django.utils import timezone
        
        user = request.user
        last_month = timezone.now() - datetime.timedelta(days=30)
        
        stats = {
            'total_favorites': user.favorites.count(),
            'favorites_last_month': user.favorites.filter(
                added_at__gte=last_month
            ).count(),
        }
        
        return JsonResponse(stats)
    
    return HttpResponseForbidden()


# ============= ДОПОЛНИТЕЛЬНЫЕ СТРАНИЦЫ =============

@login_required
def user_orders(request):
    """Страница с заказами пользователя."""
    orders = []
    try:
        from orders.models import Order
        orders = Order.objects.filter(user=request.user).prefetch_related('orderitem_set__kitchen').order_by('-created_at')
    except:
        pass
    
    return render(request, 'accounts/user_orders.html', {
        'orders': orders,
        'title': 'Мои заказы'
    })
