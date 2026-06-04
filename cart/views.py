from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart
from catalog.models import Kitchen

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def add_to_cart(request, kitchen_id):
    kitchen = get_object_or_404(Kitchen, id=kitchen_id)
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        kitchen=kitchen,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f'Кухня "{kitchen.name}" добавлена в корзину')
    return redirect('cart')

@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Товар удален из корзины')
    return redirect('cart')

@login_required
def update_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart')