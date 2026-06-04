# accounts/apps.py
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        # Импортируем сигналы
        import accounts.signals
        
        # Также можно создать каталог для аватаров при запуске
        import os
        from django.conf import settings
        
        media_root = settings.MEDIA_ROOT
        avatars_dir = os.path.join(media_root, 'avatars')
        
        if not os.path.exists(avatars_dir):
            os.makedirs(avatars_dir, exist_ok=True)
            print(f"Создана директория для аватаров: {avatars_dir}")