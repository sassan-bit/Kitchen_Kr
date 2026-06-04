from django.db import models
from django.contrib.auth.models import User
from catalog.models import Kitchen

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, verbose_name="Кухня")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.kitchen.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.kitchen.name}"

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"