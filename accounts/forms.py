# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'example@mail.com'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Введите имя пользователя',
                'autofocus': True
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Минимум 8 символов'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Повторите пароль'
            }),
        }
    
    def save(self, commit=True):
        # Сохраняем пользователя через стандартный метод
        # UserCreationForm.save() автоматически установит пароль
        user = super().save(commit=False)
        # Устанавливаем email
        user.email = self.cleaned_data.get('email', '')
        
        if commit:
            # Сохраняем пользователя
            # ВАЖНО: UserCreationForm.save(commit=True) автоматически вызывает set_password
            # Но мы используем commit=False, поэтому нужно вызвать set_password вручную
            user.set_password(self.cleaned_data['password1'])
            user.save()
        
        return user

class CustomAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=False)

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'phone_number', 'birth_date', 'address']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }