from django.contrib.auth.models import AbstractUser
from django.db import models


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Активация пройдена?')
    send_messages = models.BooleanField(default=True, verbose_name='Оповещать о новых комментариях?')

    class Meta:
        pass
