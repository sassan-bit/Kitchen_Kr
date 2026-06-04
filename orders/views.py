from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from cart.models import Cart
from catalog.models import Kitchen

@login_required
def order_list(request):
    """Список заказов пользователя"""
    orders = Order.objects.filter(user=request.user).prefetch_related('orderitem_set__kitchen').order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def create_order(request):
    """Создание заказа из корзины"""
    # Получаем товары из корзины пользователя
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items:
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('cart')
    
    if request.method == 'POST':
        # Получаем данные из формы
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        notes = request.POST.get('notes', '')
        
        # Рассчитываем общую сумму
        total_price = sum(item.total_price() for item in cart_items)
        
        # Создаем заказ
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            address=address,
            phone=phone,
            status='new'
        )
        
        # Создаем элементы заказа
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                kitchen=item.kitchen,
                quantity=item.quantity,
                price=item.kitchen.price * item.quantity
            )
        
        # Очищаем корзину
        cart_items.delete()
        
        messages.success(request, f'Заказ #{order.id} успешно оформлен!')
        return redirect('order_list')
    
    # GET запрос - показываем форму
    total_price = sum(item.total_price() for item in cart_items)
    return render(request, 'orders/create_order.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })