"""
Команда для установки пароля пользователю.
Использование: python manage.py set_user_password username password
Пример: python manage.py set_user_password admin admin123
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Устанавливает пароль для пользователя'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Имя пользователя')
        parser.add_argument('password', type=str, help='Новый пароль')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'Пользователь "{username}" не найден')
        
        # Устанавливаем пароль
        user.set_password(password)
        user.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'Пароль успешно установлен для пользователя "{username}"')
        )
        self.stdout.write(
            self.style.WARNING(f'Новый пароль: {password}')
        )

