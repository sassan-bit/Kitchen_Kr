from django.db import models

class ContactInfo(models.Model):
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    address = models.TextField(verbose_name="Адрес")
    working_hours = models.CharField(max_length=100, verbose_name="Режим работы", default="Пн-Пт 9:00-18:00")

    def __str__(self):
        return "Контактная информация"

    class Meta:
        verbose_name = "Контактная информация"
        verbose_name_plural = "Контактная информация"

class Feedback(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    is_processed = models.BooleanField(default=False, verbose_name="Обработано")

    def __str__(self):
        return f"{self.name} - {self.email}"

    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратная связь"