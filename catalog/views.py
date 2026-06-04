from django.shortcuts import render, get_object_or_404
from django.db import models
from .models import Kitchen


def catalog(request):
    from comments.models import Comment
    from django.db.models import Avg, Count
    
    # Получаем все кухни
    kitchens = Kitchen.objects.all()

    # Фильтрация по цене (из GET-параметров)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        kitchens = kitchens.filter(price__gte=min_price)
    if max_price:
        kitchens = kitchens.filter(price__lte=max_price)

    # Сортировка (из GET-параметров)
    sort = request.GET.get('sort', 'default')

    if sort == 'price_asc':
        kitchens = kitchens.order_by('price')
    elif sort == 'price_desc':
        kitchens = kitchens.order_by('-price')
    elif sort == 'name':
        kitchens = kitchens.order_by('name')
    elif sort == 'newest':
        kitchens = kitchens.order_by('-created_at')

    # Рассчитываем минимальную и максимальную цены для фильтров
    if kitchens.exists():
        min_price_range = int(kitchens.aggregate(models.Min('price'))['price__min'])
        max_price_range = int(kitchens.aggregate(models.Max('price'))['price__max'])
    else:
        min_price_range = 0
        max_price_range = 100000

    # ids избранных кухонь текущего пользователя для подсветки кнопок
    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(
            request.user.favorites.values_list('kitchen_id', flat=True)
        )
    
    # Получаем статистику комментариев для каждой кухни
    kitchen_ids = list(kitchens.values_list('id', flat=True))
    if kitchen_ids:
        comments_stats = Comment.objects.filter(kitchen_id__in=kitchen_ids).values('kitchen_id').annotate(
            avg_rating=Avg('rating'),
            comment_count=Count('id')
        )
        
        # Создаем словарь для быстрого доступа
        comments_dict = {}
        for stat in comments_stats:
            comments_dict[stat['kitchen_id']] = {
                'avg_rating': round(stat['avg_rating'], 1) if stat['avg_rating'] else 0,
                'count': stat['comment_count']
            }
    else:
        comments_dict = {}

    return render(
        request,
        'catalog/catalog.html',
        {
            'kitchens': kitchens,
            'min_price_range': min_price_range,
            'max_price_range': max_price_range,
            'current_sort': sort,
            'current_min': min_price,
            'current_max': max_price,
            'favorite_ids': favorite_ids,
            'comments_dict': comments_dict,
        },
    )


def kitchen_detail(request, kitchen_id):
    """Детальная страница кухни"""
    from comments.models import Comment
    
    kitchen = get_object_or_404(Kitchen, id=kitchen_id)

    is_favorite = False
    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(
            request.user.favorites.values_list('kitchen_id', flat=True)
        )
        is_favorite = kitchen_id in favorite_ids

    # Получаем комментарии для этой кухни
    comments = Comment.objects.filter(kitchen=kitchen).order_by('-created_at')[:5]
    
    # Рассчитываем средний рейтинг
    avg_rating = comments.aggregate(models.Avg('rating'))['rating__avg'] or 0
    comment_count = comments.count()

    return render(
        request,
        'catalog/kitchen_detail.html',
        {
            'kitchen': kitchen,
            'is_favorite': is_favorite,
            'favorite_ids': favorite_ids,
            'comments': comments,
            'avg_rating': round(avg_rating, 1),
            'comment_count': comment_count,
        },
    )

def home(request):
    """Главная страница с промо-слайдером"""
    # Получаем все кухни для горизонтальной ленты (или последние 12)
    all_kitchens = Kitchen.objects.order_by('-created_at')[:12]
    
    # Получаем 4 самые новые кухни для слайдера
    featured_kitchens = Kitchen.objects.order_by('-created_at')[:4]
    
    # Получаем кухни для разных разделов
    premium_kitchens = Kitchen.objects.filter(price__gte=150000)[:6]
    budget_kitchens = Kitchen.objects.filter(price__lte=80000)[:6]
    
    # IDs избранных кухонь для подсветки
    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(
            request.user.favorites.values_list('kitchen_id', flat=True)
        )
    
    return render(request, 'catalog/home.html', {
        'featured_kitchens': all_kitchens,  # Используем все для ленты
        'premium_kitchens': premium_kitchens,
        'budget_kitchens': budget_kitchens,
        'favorite_ids': favorite_ids,
    })