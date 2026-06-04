from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactInfo
from .forms import FeedbackForm


def contacts(request):
    contact_info = ContactInfo.objects.first()
    form = FeedbackForm()

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Получаем очищенные данные из формы
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Вывод данных в консоль
            print("=" * 50)
            print("ФОРМА ОБРАТНОЙ СВЯЗИ")
            print("=" * 50)
            print(f"Имя: {name}")
            print(f"Email: {email}")
            print(f"Сообщение: {message}")
            print("=" * 50)

            # Сохраняем в БД
            form.save()

            messages.success(request, 'Спасибо! Ваше сообщение отправлено. Мы ответим вам в течение 24 часов.')
            return redirect('contacts')

    return render(request, 'contacts/contacts.html', {
        'contact_info': contact_info,
        'form': form,
    })