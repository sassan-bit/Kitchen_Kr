from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from catalog.models import Kitchen, KitchenImage


class KitchenModelTest(TestCase):
    def test_kitchen_creation(self):
        """Тест создания кухни"""
        kitchen = Kitchen.objects.create(
            name='Кухня Модерн',
            description='Современная кухня в стиле модерн',
            price=150000
        )
        self.assertEqual(kitchen.name, 'Кухня Модерн')
        self.assertEqual(kitchen.price, 150000)
        self.assertIsNotNone(kitchen.created_at)

    def test_kitchen_str_method(self):
        """Тест строкового представления модели"""
        kitchen = Kitchen.objects.create(
            name='Кухня Классик',
            price=200000
        )
        self.assertEqual(str(kitchen), 'Кухня Классик')

    def test_kitchen_ordering(self):
        """Тест сортировки кухонь по дате создания"""
        kitchen1 = Kitchen.objects.create(
            name='Кухня 1',
            price=100000
        )
        kitchen2 = Kitchen.objects.create(
            name='Кухня 2',
            price=120000
        )
        kitchens = list(Kitchen.objects.all())
        # Последняя созданная должна быть первой (ordering = ['-created_at'])
        self.assertEqual(kitchens[0], kitchen2)


class KitchenImageModelTest(TestCase):
    def setUp(self):
        """Создание тестовой кухни"""
        self.kitchen = Kitchen.objects.create(
            name='Тестовая кухня',
            price=100000
        )

    def test_kitchen_image_creation(self):
        """Тест создания изображения кухни"""
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x00\x01\x02\x03',
            content_type='image/jpeg'
        )
        kitchen_image = KitchenImage.objects.create(
            kitchen=self.kitchen,
            image=image,
            alt_text='Тестовое изображение'
        )
        self.assertEqual(kitchen_image.kitchen, self.kitchen)
        self.assertEqual(kitchen_image.alt_text, 'Тестовое изображение')

    def test_kitchen_image_auto_alt_text(self):
        """Тест автоматического заполнения alt_text"""
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x00\x01\x02\x03',
            content_type='image/jpeg'
        )
        kitchen_image = KitchenImage.objects.create(
            kitchen=self.kitchen,
            image=image
        )
        # alt_text должен быть автоматически заполнен
        self.assertIn('Дополнительное фото кухни', kitchen_image.alt_text)


class CatalogViewTest(TestCase):
    def setUp(self):
        """Создание тестовых данных"""
        self.kitchen1 = Kitchen.objects.create(
            name='Кухня 1',
            price=100000,
            description='Описание 1'
        )
        self.kitchen2 = Kitchen.objects.create(
            name='Кухня 2',
            price=200000,
            description='Описание 2'
        )

    def test_catalog_page_loads(self):
        """Тест загрузки страницы каталога"""
        from django.test import Client
        client = Client()
        response = client.get('/catalog/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Кухня 1')
        self.assertContains(response, 'Кухня 2')

    def test_kitchen_detail_page(self):
        """Тест детальной страницы кухни"""
        from django.test import Client
        client = Client()
        response = client.get(f'/catalog/{self.kitchen1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Кухня 1')
        self.assertContains(response, '100000')
