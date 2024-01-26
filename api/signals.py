from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

user_create_signal = Signal()
token_create_signal = Signal()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def generate_token(sender, instance, created, **kwargs):
    if created:
        token, created = Token.objects.get_or_create(user=instance)
        token_create_signal.send(
            sender=instance.__class__, instance=instance, token=token
        )


user_create_signal.connect(generate_token, sender=settings.AUTH_USER_MODEL)
