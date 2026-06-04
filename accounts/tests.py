from django.test import TestCase, Client
from django.contrib.auth.models import User
from catalog.models import Kitchen
from accounts.models import UserProfile, Favorite


class UserProfileModelTest(TestCase):
    def setUp(self):
        """Создание тестового пользователя"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

    def test_user_profile_creation(self):
        """Тест создания профиля пользователя"""
        # Удаляем профиль если он был создан middleware
        UserProfile.objects.filter(user=self.user).delete()
        profile = UserProfile.objects.create(
            user=self.user,
            phone_number='+79991234567',
            address='Москва, ул. Тестовая, д. 1'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.phone_number, '+79991234567')
        self.assertIsNotNone(profile.created_at)

    def test_user_profile_str_method(self):
        """Тест строкового представления модели"""
        # Используем get_or_create, так как профиль может быть создан middleware
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.assertIn('testuser', str(profile))

    def test_user_profile_get_initials(self):
        """Тест получения инициалов пользователя"""
        self.user.first_name = 'Иван'
        self.user.last_name = 'Иванов'
        self.user.save()
        # Используем get_or_create, так как профиль может быть создан middleware
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        initials = profile.get_initials()
        self.assertEqual(initials, 'ИИ')


class FavoriteModelTest(TestCase):
    def setUp(self):
        """Создание тестовых данных"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.kitchen = Kitchen.objects.create(
            name='Тестовая кухня',
            price=100000
        )

    def test_favorite_creation(self):
        """Тест создания записи в избранном"""
        favorite = Favorite.objects.create(
            user=self.user,
            kitchen=self.kitchen,
            note='Нравится дизайн',
            priority=2
        )
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.kitchen, self.kitchen)
        self.assertEqual(favorite.priority, 2)

    def test_favorite_unique_together(self):
        """Тест что один пользователь не может дважды добавить одну кухню"""
        Favorite.objects.create(
            user=self.user,
            kitchen=self.kitchen
        )
        # Попытка создать дубликат должна вызвать ошибку
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Favorite.objects.create(
                user=self.user,
                kitchen=self.kitchen
            )

    def test_favorite_str_method(self):
        """Тест строкового представления модели"""
        favorite = Favorite.objects.create(
            user=self.user,
            kitchen=self.kitchen
        )
        self.assertIn('testuser', str(favorite))
        self.assertIn('Тестовая кухня', str(favorite))


class AccountsViewTest(TestCase):
    def setUp(self):
        """Создание тестовых данных"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.kitchen = Kitchen.objects.create(
            name='Тестовая кухня',
            price=100000
        )

    def test_profile_page_requires_login(self):
        """Тест что страница профиля требует авторизации"""
        response = self.client.get('/accounts/profile/')
        # Должен быть редирект на страницу логина
        self.assertEqual(response.status_code, 302)

    def test_profile_page_authorized(self):
        """Тест доступа к странице профиля авторизованным пользователем"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
