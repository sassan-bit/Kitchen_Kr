from django.test import TestCase
from django.contrib.auth.models import User
from catalog.models import Kitchen
from comments.models import Comment


class CommentModelTest(TestCase):
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

    def test_comment_creation(self):
        """Тест создания комментария"""
        comment = Comment.objects.create(
            user=self.user,
            kitchen=self.kitchen,
            text='Отличная кухня!',
            rating=5
        )
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.kitchen, self.kitchen)
        self.assertEqual(comment.text, 'Отличная кухня!')
        self.assertEqual(comment.rating, 5)
        self.assertIsNotNone(comment.created_at)

    def test_comment_str_method(self):
        """Тест строкового представления модели"""
        comment = Comment.objects.create(
            user=self.user,
            kitchen=self.kitchen,
            text='Хорошая кухня'
        )
        self.assertIn('testuser', str(comment))
        self.assertIn('Тестовая кухня', str(comment))

    def test_comment_default_rating(self):
        """Тест значения рейтинга по умолчанию"""
        comment = Comment.objects.create(
            user=self.user,
            kitchen=self.kitchen,
            text='Комментарий без рейтинга'
        )
        # По умолчанию rating = 5
        self.assertEqual(comment.rating, 5)
