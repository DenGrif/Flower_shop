from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
import requests
from django.conf import settings


@receiver(post_save, sender=Order)
def send_telegram_notification(sender, instance, created, **kwargs):
    if created:
        token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID
        message = f"Новый заказ #{instance.id}\n"
        message += f"Клиент: {instance.user.name}\n"
        message += f"Адрес: {instance.delivery_address}\n"
        message += f"Дата: {instance.delivery_date}\n"
        message += f"Время: {instance.delivery_time}\n"
        message += f"Комментарий: {instance.comments}\n"

        # Отправка сообщения
        requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={
            'chat_id': chat_id,
            'text': message
        })

        # Отправка изображений товаров
        for item in instance.orderitem_set.all():
            if item.product.image:
                image_url = f"{settings.SITE_DOMAIN}{item.product.image.url}"
                requests.post(f'https://api.telegram.org/bot{token}/sendPhoto', data={
                    'chat_id': chat_id,
                    'photo': image_url,
                    'caption': item.product.name
                })