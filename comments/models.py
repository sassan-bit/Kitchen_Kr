from django.db import models
from django.contrib.auth.models import User
from catalog.models import Kitchen

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, verbose_name="Кухня")
    text = models.TextField(verbose_name="Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    rating = models.PositiveIntegerField(default=5, verbose_name="Рейтинг", help_text="От 1 до 5")

    def __str__(self):
        return f"{self.user.username} - {self.kitchen.name}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"