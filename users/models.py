from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    deadline = models.DateField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def days_left(self):
        return (self.deadline - date.today()).days

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Поле для хранения ID чата в Телеграме
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)
    # Поле со случайным кодом для безопасной привязки бота
    tg_auth_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Профиль {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()