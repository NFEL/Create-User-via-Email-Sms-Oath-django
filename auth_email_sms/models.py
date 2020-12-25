import os
import uuid
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.core.mail import EmailMessage
from django.core.cache import cache


class User(AbstractUser):
    user_uuid = models.CharField(max_length=36, blank=True)

    def save(self,*args, **kwargs):
        if not self.id:
            self.username = self.email
            self.set_unusable_password()
            self.is_active = False
        return super().save(*args,**kwargs)
            
    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['email'], name='make Email unique')]


def reic(sender, instance, *args, **kwargs):    
    if not cache.get(instance.user_uuid) and not instance.is_active:
        instance.user_uuid = uuid.uuid4()
        msg = EmailMessage(
            'Signup via Email',
            f'<a href="http://127.0.0.1:8000/verificationcode/{instance.user_uuid}">Verify me</a>',
            os.getenv('EMAIL_USERNAME'),
            [instance.email,])
        msg.content_subtype = "html"  
        msg.send()
        instance.save()
        cache.set(instance.user_uuid, instance, timeout=60*2)
    

post_save.connect(reic, weak=False,sender=User)
