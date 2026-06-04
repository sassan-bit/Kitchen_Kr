# accounts/models.py

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import io


class UserProfile(models.Model):
    """
    Модель для расширения стандартной модели User.
    Содержит дополнительные данные пользователя.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Пользователь"
    )
    
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите изображение профиля"
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Номер телефона"
    )
    
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата рождения"
    )
    
    address = models.TextField(
        blank=True,
        verbose_name="Адрес",
        help_text="Ваш постоянный адрес"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания профиля"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    # Используем стандартный менеджер
    objects = models.Manager()

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
        ordering = ['-created_at']

    def __str__(self):
        return f"Профиль: {self.user.username}"

    def save(self, *args, **kwargs):
        """Переопределяем метод save для обработки изображения."""
        # Сохраняем модель сначала
        super().save(*args, **kwargs)
        
        # Обрабатываем аватар если он есть
        if self.avatar:
            self._compress_avatar()

    def _compress_avatar(self):
        """Сжимает аватар до оптимального размера."""
        try:
            # Открываем изображение
            img_path = self.avatar.path
            
            # Проверяем, существует ли файл
            if not os.path.exists(img_path):
                return
                
            img = Image.open(img_path)
            
            # Конвертируем в RGB если нужно
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Максимальные размеры
            max_size = (300, 300)
            
            # Изменяем размер если изображение больше
            if img.height > 300 or img.width > 300:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Сохраняем с оптимизацией
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG', quality=85, optimize=True)
                
                # Сохраняем обратно в файл
                self.avatar.save(
                    os.path.basename(self.avatar.name),
                    ContentFile(img_io.getvalue()),
                    save=False
                )
                super().save(update_fields=['avatar'])
                
        except Exception as e:
            # В случае ошибки просто пропускаем сжатие
            print(f"Ошибка при сжатии изображения: {e}")

    def get_avatar_url(self):
        """
        Безопасно возвращает URL аватара.
        Проверяет наличие файла и возвращает URL или дефолтное изображение.
        """
        try:
            # Проверяем, есть ли файл аватара
            if self.avatar and self.avatar.name:
                # Проверяем, существует ли файл в хранилище
                if default_storage.exists(self.avatar.name):
                    return self.avatar.url
        except (ValueError, AttributeError):
            # Если поле есть, но файла нет
            pass
        except Exception as e:
            # Ловим любые другие исключения
            print(f"Ошибка при получении URL аватара: {e}")
        
        # Возвращаем дефолтное изображение
        return self.get_default_avatar_url()

    @staticmethod
    def get_default_avatar_url():
        """Возвращает URL дефолтного аватара."""
        return '/static/images/default-avatar.png'

    def avatar_exists(self):
        """Проверяет, существует ли файл аватара."""
        try:
            return bool(
                self.avatar and 
                self.avatar.name and 
                default_storage.exists(self.avatar.name)
            )
        except:
            return False

    @property
    def avatar_display_url(self):
        """Свойство для удобного доступа к URL аватара."""
        return self.get_avatar_url()

    @property
    def full_name(self):
        """Возвращает полное имя пользователя."""
        name = f"{self.user.first_name} {self.user.last_name}".strip()
        return name if name else self.user.username

    @property
    def age(self):
        """Возвращает возраст пользователя если указана дата рождения."""
        from datetime import date
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year
            # Проверяем, был ли уже день рождения в этом году
            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                age -= 1
            return age
        return None

    @property
    def member_since_days(self):
        """Возвращает сколько дней пользователь с нами."""
        from datetime import date
        days = (date.today() - self.created_at.date()).days
        return days

    def get_profile_completion_percentage(self):
        """Возвращает процент заполнения профиля."""
        fields = [
            self.user.first_name,  # Имя
            self.user.last_name,   # Фамилия
            self.user.email,       # Email
            self.phone_number,     # Телефон
            self.address,          # Адрес
            self.birth_date,       # Дата рождения
            self.avatar,           # Аватар
        ]
        
        filled = sum(1 for field in fields if field)
        total = len(fields)
        
        return int((filled / total) * 100)

    def get_initials(self):
        """Возвращает инициалы пользователя для дефолтного аватара."""
        initials = ""
        if self.user.first_name:
            initials += self.user.first_name[0].upper()
        if self.user.last_name:
            initials += self.user.last_name[0].upper()
        if not initials:
            initials = self.user.username[0:2].upper()
        return initials

    def get_activity_summary(self):
        """Возвращает краткую статистику активности пользователя."""
        from datetime import datetime, timedelta
        from django.db.models import Count
        
        last_month = datetime.now() - timedelta(days=30)
        
        return {
            'favorites_count': self.user.favorites.count(),
            'recent_favorites': self.user.favorites.filter(
                added_at__gte=last_month
            ).count(),
            'last_activity': self.updated_at.strftime('%d.%m.%Y %H:%M')
        }

    def clean(self):
        """Валидация данных перед сохранением."""
        from django.core.exceptions import ValidationError
        
        # Проверяем телефон (только цифры, можно с плюсом)
        if self.phone_number and not self.phone_number.replace('+', '').isdigit():
            raise ValidationError({'phone_number': 'Номер телефона должен содержать только цифры и знак +'})
        
        # Проверяем дату рождения (не будущее и не слишком старое)
        if self.birth_date:
            from datetime import date
            today = date.today()
            if self.birth_date > today:
                raise ValidationError({'birth_date': 'Дата рождения не может быть в будущем'})
            
            age = today.year - self.birth_date.year
            if age > 120:
                raise ValidationError({'birth_date': 'Пожалуйста, проверьте дату рождения'})

    def update_profile(self, **kwargs):
        """Обновляет профиль с указанными полями."""
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)
        self.save()

    def generate_avatar_color(self):
        """Генерирует цвет для дефолтного аватара на основе имени пользователя."""
        import hashlib
        
        # Создаем хэш от имени пользователя для детерминированного цвета
        hash_object = hashlib.md5(self.user.username.encode())
        hash_hex = hash_object.hexdigest()
        
        # Берем первые 6 символов для цвета
        color = f"#{hash_hex[:6]}"
        
        # Делаем цвет немного мягче
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Осветляем цвет
        r = min(r + 40, 255)
        g = min(g + 40, 255)
        b = min(b + 40, 255)
        
        return f"#{r:02x}{g:02x}{b:02x}"


class Favorite(models.Model):
    """
    Модель для хранения избранных товаров (кухонь).
    Пользователь может добавлять/удалять товары в избранное.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="Пользователь"
    )
    
    kitchen = models.ForeignKey(
        'catalog.Kitchen',
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name="Кухня"
    )
    
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    
    note = models.TextField(
        blank=True,
        verbose_name="Заметка",
        help_text="Личная заметка об этом товаре"
    )
    
    priority = models.PositiveSmallIntegerField(
        default=1,
        choices=[(1, 'Низкий'), (2, 'Средний'), (3, 'Высокий')],
        verbose_name="Приоритет"
    )

    class Meta:
        verbose_name = "Избранный товар"
        verbose_name_plural = "Избранные товары"
        unique_together = ('user', 'kitchen')
        ordering = ['-priority', '-added_at']
        indexes = [
            models.Index(fields=['user', 'added_at']),
            models.Index(fields=['kitchen']),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.kitchen.name}"

    @property
    def kitchen_price(self):
        """Возвращает текущую цену кухни (актуальную)."""
        return self.kitchen.price if self.kitchen else 0

    @property
    def kitchen_image(self):
        """Возвращает изображение кухни."""
        if self.kitchen and self.kitchen.image:
            return self.kitchen.image.url
        return '/static/images/default-kitchen.png'


class UserActivity(models.Model):
    """
    Модель для отслеживания активности пользователя.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name="Пользователь"
    )
    
    activity_type = models.CharField(
        max_length=50,
        choices=[
            ('login', 'Вход в систему'),
            ('registration', 'Регистрация'),
            ('view_product', 'Просмотр товара'),
            ('add_to_favorites', 'Добавление в избранное'),
            ('remove_from_favorites', 'Удаление из избранного'),
            ('update_profile', 'Обновление профиля'),
            ('add_to_cart', 'Добавление в корзину'),
            ('purchase', 'Покупка'),
            ('review', 'Оставление отзыва'),
        ],
        verbose_name="Тип активности"
    )
    
    details = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Детали активности"
    )
    
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="IP адрес"
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата активности"
    )

    class Meta:
        verbose_name = "Активность пользователя"
        verbose_name_plural = "Активности пользователей"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"

    def get_description(self):
        """Возвращает человеко-читаемое описание активности."""
        descriptions = {
            'login': 'Вы вошли в систему',
            'registration': 'Вы зарегистрировались',
            'view_product': 'Вы просмотрели товар',
            'add_to_favorites': 'Вы добавили товар в избранное',
            'remove_from_favorites': 'Вы удалили товар из избранного',
            'update_profile': 'Вы обновили профиль',
            'add_to_cart': 'Вы добавили товар в корзину',
            'purchase': 'Вы совершили покупку',
            'review': 'Вы оставили отзыв',
        }
        return descriptions.get(self.activity_type, 'Неизвестное действие')

    def get_icon(self):
        """Возвращает иконку для типа активности."""
        icons = {
            'login': 'fas fa-sign-in-alt',
            'registration': 'fas fa-user-plus',
            'view_product': 'fas fa-eye',
            'add_to_favorites': 'fas fa-heart',
            'remove_from_favorites': 'fas fa-heart-broken',
            'update_profile': 'fas fa-user-edit',
            'add_to_cart': 'fas fa-shopping-cart',
            'purchase': 'fas fa-shopping-bag',
            'review': 'fas fa-star',
        }
        return icons.get(self.activity_type, 'fas fa-info-circle')


# ============= СИГНАЛЫ =============

# Сигнал отключен - профиль создается вручную в view для надежности
# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     pass


@receiver(post_save, sender=Favorite)
def log_favorite_activity(sender, instance, created, **kwargs):
    """
    Логирует добавление товара в избранное.
    """
    if created:
        try:
            UserActivity.objects.create(
                user=instance.user,
                activity_type='add_to_favorites',
                details={
                    'kitchen_id': instance.kitchen.id,
                    'kitchen_name': instance.kitchen.name,
                    'price': float(instance.kitchen.price) if instance.kitchen.price else 0
                }
            )
        except Exception as e:
            # Не критично, если не удалось залогировать
            print(f"Error logging favorite activity: {e}")


@receiver(models.signals.pre_delete, sender=Favorite)
def log_remove_favorite_activity(sender, instance, **kwargs):
    """
    Логирует удаление товара из избранного.
    """
    try:
        UserActivity.objects.create(
            user=instance.user,
            activity_type='remove_from_favorites',
            details={
                'kitchen_id': instance.kitchen.id,
                'kitchen_name': instance.kitchen.name
            }
        )
    except Exception as e:
        # Не критично, если не удалось залогировать
        print(f"Error logging remove favorite activity: {e}")


@receiver(post_save, sender=UserProfile)
def log_profile_update_activity(sender, instance, created, **kwargs):
    """
    Логирует обновление профиля.
    """
    if not created:  # Только при обновлении, не при создании
        try:
            update_fields = kwargs.get('update_fields')
            if update_fields is None:
                # Если update_fields не переданы, логируем без списка полей
                update_fields_list = []
            else:
                update_fields_list = list(update_fields)

            UserActivity.objects.create(
                user=instance.user,
                activity_type='update_profile',
                details={
                    'fields_updated': update_fields_list,
                    'avatar_updated': bool(instance.avatar)
                }
            )
        except Exception as e:
            # Не критично, если не удалось залогировать
            print(f"Error logging profile update activity: {e}")


# ============= МЕНЕДЖЕРЫ =============

# Кастомный менеджер отключен, используем стандартный для надежности
# class UserProfileManager(models.Manager):
#     """Кастомный менеджер для UserProfile."""
#     pass


# ============= УТИЛИТЫ =============

def create_default_avatar_for_user(user):
    """
    Создает дефолтный аватар для пользователя с его инициалами.
    В реальном проекте здесь была бы генерация SVG или PNG.
    """
    # В демо-версии просто возвращаем URL дефолтного аватара
    return UserProfile.get_default_avatar_url()


def migrate_existing_users():
    """
    Утилита для миграции существующих пользователей.
    Создает профили для пользователей без профилей.
    """
    from django.contrib.auth.models import User
    
    users_without_profiles = User.objects.filter(profile__isnull=True)
    
    for user in users_without_profiles:
        UserProfile.objects.create(user=user)
        print(f"Создан профиль для пользователя: {user.username}")
    
    return len(users_without_profiles)