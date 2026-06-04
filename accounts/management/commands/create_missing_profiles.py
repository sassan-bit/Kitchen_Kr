"""
Команда для создания профилей для всех пользователей, у которых их нет.
Использование: python manage.py create_missing_profiles
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Создает профили для всех пользователей, у которых их нет'

    def handle(self, *args, **options):
        # Импортируем здесь, чтобы избежать проблем с циклическими импортами
        from accounts.models import UserProfile
        
        # Получаем всех пользователей
        all_users = User.objects.all()
        count = 0
        
        for user in all_users:
            try:
                # Проверяем, есть ли профиль
                try:
                    user.profile
                    # Профиль существует, пропускаем
                    continue
                except UserProfile.DoesNotExist:
                    # Профиля нет, создаем
                    profile = UserProfile.objects.create(user=user)
                    count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Создан профиль для пользователя: {user.username}')
                    )
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при создании профиля для {user.username}: {e}')
                )
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('Все пользователи уже имеют профили!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nВсего создано профилей: {count}')
            )

