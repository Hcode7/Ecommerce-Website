from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=User)
def create_profile_post_save(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        print('Profile created!')

@receiver(post_save, sender=User)
def save_profile_post_save(sender, instance, **kwargs):
    instance.profile.save()
    print('Profile saved!')