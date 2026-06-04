from django.test import TestCase, Client
from django.contrib.auth.models import User
from catalog.models import Kitchen
from cart.models import Cart
from orders.models import Order, OrderItem


class OrderModelTest(TestCase):
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

    def test_order_creation(self):
        """Тест создания заказа"""
        order = Order.objects.create(
            user=self.user,
            total_price=100000,
            status='new',
            address='Москва, ул. Тестовая, д. 1',
            phone='+79991234567'
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'new')
        self.assertEqual(order.total_price, 100000)
        self.assertIsNotNone(order.created_at)

    def test_order_str_method(self):
        """Тест строкового представления модели"""
        order = Order.objects.create(
            user=self.user,
            total_price=100000,
            status='new'
        )
        self.assertIn('Заказ', str(order))
        self.assertIn('testuser', str(order))

    def test_order_item_total(self):
        """Тест расчета стоимости элемента заказа"""
        order = Order.objects.create(
            user=self.user,
            total_price=200000,
            status='new'
        )
        order_item = OrderItem.objects.create(
            order=order,
            kitchen=self.kitchen,
            quantity=2,
            price=100000
        )
        # 100000 * 2 = 200000
        self.assertEqual(order_item.item_total(), 200000)

    def test_order_with_coordinates(self):
        """Тест создания заказа с координатами"""
        order = Order.objects.create(
            user=self.user,
            total_price=100000,
            status='new',
            latitude=55.7558,
            longitude=37.6173
        )
        self.assertEqual(order.latitude, 55.7558)
        self.assertEqual(order.longitude, 37.6173)


class OrderViewTest(TestCase):
    def setUp(self):
        """Создание тестовых данных"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='buyer',
            password='testpass123',
            email='buyer@test.com'
        )
        self.kitchen = Kitchen.objects.create(
            name='Тестовая кухня',
            price=100000
        )

    def test_create_order_requires_login(self):
        """Тест что оформление заказа требует авторизации"""
        response = self.client.get('/orders/create/')
        # Должен быть редирект на страницу логина
        self.assertEqual(response.status_code, 302)

    def test_create_order_updates_cart(self):
        """Тест что оформление заказа очищает корзину"""
        self.client.login(username='buyer', password='testpass123')
        
        # Добавляем товар в корзину
        Cart.objects.create(
            user=self.user,
            kitchen=self.kitchen,
            quantity=1
        )
        
        # Оформляем заказ
        response = self.client.post('/orders/create/', {
            'address': 'Москва, ул. Тестовая, д. 1',
            'phone': '+79991234567',
            'latitude': '55.7558',
            'longitude': '37.6173'
        })
        
        # Проверяем что заказ создан
        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.total_price, 100000)
        
        # Проверяем что корзина очищена
        cart_items = Cart.objects.filter(user=self.user)
        self.assertEqual(cart_items.count(), 0)
