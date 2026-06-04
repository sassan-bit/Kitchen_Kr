from django.db import models
from django.contrib.auth.models import User
from catalog.models import Kitchen

class Order(models.Model):
    """Модель заказа"""
    STATUS_CHOICES = [
        ('new', '🆕 Новый'),
        ('processing', '🔄 В обработке'),
        ('completed', '✅ Завершен'),
        ('cancelled', '❌ Отменен'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая цена")
    
    # Контактная информация
    address = models.TextField(verbose_name="Адрес доставки", blank=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True)
    
    # Координаты для Яндекс.Карт (добавлены для интеграции с картами)
    latitude = models.FloatField(verbose_name="Широта", null=True, blank=True)
    longitude = models.FloatField(verbose_name="Долгота", null=True, blank=True)
    
    # Статус и даты
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new', 
        verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    # Примечания
    notes = models.TextField(verbose_name="Примечания к заказу", blank=True)
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.user.username}"
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

class OrderItem(models.Model):
    """Элемент заказа (связь многие-ко-многим между Order и Kitchen)"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    kitchen = models.ForeignKey(Kitchen, on_delete=models.CASCADE, verbose_name="Кухня")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")
    
    def item_total(self):
        """Общая стоимость элемента заказа"""
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.kitchen.name} x {self.quantity}"
    
    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"