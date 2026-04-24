from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """Категорії статусів: Applied, Interview, Offer, Rejected"""
    name = models.CharField(max_length=100, verbose_name="Назва статусу")

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статуси"
        ordering = ['name']

    def __str__(self):
        return self.name


class JobApplication(models.Model):
    """Сама вакансія"""
    title = models.CharField(max_length=200, verbose_name="Посада")
    company = models.CharField(max_length=200, verbose_name="Компанія")
    url = models.URLField(blank=True, verbose_name="Посилання на вакансію")
    description = models.TextField(blank=True, verbose_name="Нотатки")

    # Зв'язок зі статусом (ForeignKey)
    status = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="applications",
        verbose_name="Статус"
    )

    # Зв'язок з користувачем (User)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Власник"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
    status_changed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата зміни статусу")


    class Meta:
        verbose_name = "Відгук на вакансію"
        verbose_name_plural = "Відгуки на вакансії"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} у {self.company}"

    def save(self, *args, **kwargs):
        if self.pk:
            old = JobApplication.objects.filter(pk=self.pk).values('status_id').first()
            if old and old['status_id'] != self.status_id:
                self.status_changed_at = timezone.now()
        super().save(*args, **kwargs)

class Event(models.Model):
    EVENT_TYPES = [
        ('interview', 'Співбесіда'),
        ('deadline', 'Дедлайн'),
        ('other', 'Інше'),
    ]

    job = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name="Вакансія"
    )
    title = models.CharField(max_length=200, verbose_name="Назва події")
    date = models.DateTimeField(verbose_name="Дата та час")
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES,
        default='other',
        verbose_name="Тип події"
    )

    class Meta:
        verbose_name = "Подія"
        verbose_name_plural = "Події"
        ordering = ['date']

    def __str__(self):
        return f"{self.title} — {self.date}"