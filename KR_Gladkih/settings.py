"""
Django settings for KR_Gladkih project.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-*w&z)9-7j1&3^)8$d#u3v0p&w8+q@0w9!6o5^s@f#b3$k!m%n4'  # Сгенерированный ключ

DEBUG = True
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.1.104',  # Локальный IP компьютера
]

# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # Для форматирования чисел (intcomma)
    
    # Мои приложения
    'accounts',
    'catalog',
    'cart',
    'orders',
    'comments',
    'contacts',
]

# ВАЖНО: AuthenticationMiddleware должен быть!
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Ваше собственное middleware
    'accounts.middleware.UserProfileMiddleware',
]

ROOT_URLCONF = 'KR_Gladkih.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # или os.path.join(BASE_DIR, 'templates')
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'KR_Gladkih.wsgi.application'

# База данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Валидация паролей
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Язык и время
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Статические файлы
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # или os.path.join(BASE_DIR, 'static')

# Медиа файлы
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Настройки входа
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'catalog'
LOGOUT_REDIRECT_URL = 'catalog'

# Настройки почты для разработки
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
PASSWORD_RESET_TIMEOUT = 86400  # 24 часа

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'