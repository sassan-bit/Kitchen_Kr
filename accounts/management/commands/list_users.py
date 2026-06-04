"""
Команда для просмотра всех пользователей и их информации.
Использование: python manage.py list_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Показывает список всех пользователей'

    def handle(self, *args, **options):
        users = User.objects.all().order_by('date_joined')
        
        if not users.exists():
            self.stdout.write(self.style.WARNING('Пользователи не найдены'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\nНайдено пользователей: {users.count()}\n'))
        self.stdout.write('=' * 80)
        
        for user in users:
            has_profile = hasattr(user, 'profile')
            password_set = bool(user.password)
            
            self.stdout.write(f'\nИмя пользователя: {user.username}')
            self.stdout.write(f'  Email: {user.email or "не указан"}')
            self.stdout.write(f'  Имя: {user.first_name or "не указано"}')
            self.stdout.write(f'  Фамилия: {user.last_name or "не указана"}')
            self.stdout.write(f'  Дата регистрации: {user.date_joined.strftime("%d.%m.%Y %H:%M")}')
            self.stdout.write(f'  Последний вход: {user.last_login.strftime("%d.%m.%Y %H:%M") if user.last_login else "никогда"}')
            self.stdout.write(f'  Пароль установлен: {"✓ Да" if password_set else "✗ Нет"}')
            self.stdout.write(f'  Профиль создан: {"✓ Да" if has_profile else "✗ Нет"}')
            self.stdout.write(f'  Статус: {"Активен" if user.is_active else "Неактивен"}')
            self.stdout.write(f'  Администратор: {"Да" if user.is_staff else "Нет"}')
            self.stdout.write('-' * 80)
        
        self.stdout.write('\n')

