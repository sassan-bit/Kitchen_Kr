from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalog.models import Kitchen
from .models import Comment

@login_required
def add_comment(request, kitchen_id):
    kitchen = get_object_or_404(Kitchen, id=kitchen_id)
    
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        rating = int(request.POST.get('rating', 5))
        
        if not text:
            messages.error(request, 'Пожалуйста, введите текст комментария')
            return redirect('kitchen_detail', kitchen_id=kitchen_id)
        
        if rating < 1 or rating > 5:
            rating = 5
        
        # Создаем комментарий
        Comment.objects.create(
            user=request.user,
            kitchen=kitchen,
            text=text,
            rating=rating
        )
        
        messages.success(request, 'Спасибо! Ваш комментарий добавлен.')
        return redirect('kitchen_detail', kitchen_id=kitchen_id)
    
    # GET запрос - показываем форму
    return render(request, 'comments/add_comment.html', {
        'kitchen': kitchen
    })

@login_required
def delete_comment(request, comment_id):
    # Пока заглушка
    messages.success(request, 'Комментарий удален')
    return redirect('catalog')