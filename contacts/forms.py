from django import forms
from .models import Feedback


class FeedbackForm(forms.ModelForm):
    """Форма обратной связи"""

    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        labels = {
            'name': 'Ваше имя',
            'email': 'Email адрес',
            'message': 'Сообщение',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше имя',
                'maxlength': '100',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.com',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше сообщение...',
                'rows': 5,
            }),
        }
