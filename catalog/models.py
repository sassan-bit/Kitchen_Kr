from django.db import models
from django.contrib.auth.models import User

class Kitchen(models.Model):
    """Модель кухни (товара)"""
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='kitchens/', verbose_name="Основное изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Кухня"
        verbose_name_plural = "Кухни"
        ordering = ['-created_at']

class KitchenImage(models.Model):
    """Модель для дополнительных фотографий кухни"""
    kitchen = models.ForeignKey(
        Kitchen, 
        on_delete=models.CASCADE, 
        related_name='images',  # Важно: позволяет обращаться kitchen.images.all()
        verbose_name="Кухня"
    )
    image = models.ImageField(
        upload_to='kitchens/gallery/', 
        verbose_name="Дополнительное фото"
    )
    alt_text = models.CharField(
        max_length=200, 
        verbose_name="Описание фото", 
        blank=True, 
        help_text="Необязательно, например: 'Вид сбоку', 'Интерьер'"
    )
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name="Порядок сортировки",
        help_text="Чем меньше число, тем раньше показывается"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата добавления"
    )
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Фотография кухни"
        verbose_name_plural = "Фотографии кухни"
    
    def __str__(self):
        if self.alt_text:
            return f"Фото: {self.alt_text} (для {self.kitchen.name})"
        return f"Фото для {self.kitchen.name}"
    
    def save(self, *args, **kwargs):
        # Автоматически заполняем alt_text, если он пустой
        if not self.alt_text:
            self.alt_text = f"Дополнительное фото кухни {self.kitchen.name}"
        super().save(*args, **kwargs)