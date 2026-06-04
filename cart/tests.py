from django.test import TestCase, Client
from django.contrib.auth.models import User
from catalog.models import Kitchen
from cart.models import Cart


class CartModelTest(TestCase):
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

    def test_cart_creation(self):
        """Тест создания записи в корзине"""
        cart_item = Cart.objects.create(
            user=self.user,
            kitchen=self.kitchen,
            quantity=2
        )
        self.assertEqual(cart_item.user, self.user)
        self.assertEqual(cart_item.kitchen, self.kitchen)
        self.assertEqual(cart_item.quantity, 2)

    def test_cart_total_price(self):
        """Тест расчета общей стоимости товара в корзине"""
        cart_item = Cart.objects.create(
            user=self.user,
            kitchen=self.kitchen,
            quantity=3
        )
        # 100000 * 3 = 300000
        self.assertEqual(cart_item.total_price(), 300000)

    def test_cart_str_method(self):
        """Тест строкового представления модели"""
        cart_item = Cart.objects.create(
            user=self.user,
            kitchen=self.kitchen,
            quantity=1
        )
        self.assertIn('testuser', str(cart_item))
        self.assertIn('Тестовая кухня', str(cart_item))


class CartViewTest(TestCase):
    def setUp(self):
        """Создание тестовых данных"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='buyer',
            password='testpass123'
        )
        self.kitchen = Kitchen.objects.create(
            name='Тестовая кухня',
            price=100000
        )

    def test_add_to_cart_requires_login(self):
        """Тест что добавление в корзину требует авторизации"""
        response = self.client.post(f'/cart/add/{self.kitchen.id}/')
        # Должен быть редирект на страницу логина
        self.assertEqual(response.status_code, 302)

    def test_add_to_cart_authorized(self):
        """Тест добавления товара в корзину авторизованным пользователем"""
        self.client.login(username='buyer', password='testpass123')
        response = self.client.post(f'/cart/add/{self.kitchen.id}/')
        # Должен быть редирект
        self.assertEqual(response.status_code, 302)
        
        # Проверка создания записи в корзине
        cart_item = Cart.objects.filter(
            user=self.user,
            kitchen=self.kitchen
        ).first()
        self.assertIsNotNone(cart_item)
        self.assertEqual(cart_item.quantity, 1)

    def test_cart_view_displays_items(self):
        """Тест отображения товаров в корзине"""
        self.client.login(username='buyer', password='testpass123')
        Cart.objects.create(
            user=self.user,
            kitchen=self.kitchen,
            quantity=2
        )
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовая кухня')
