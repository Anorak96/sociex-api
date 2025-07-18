from turtle import mode
from django.db import models
import os
from PIL import Image
from django.core.validators import FileExtensionValidator
from uuid import uuid4
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.urls import reverse

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):    
        """
        Creates and saves a User with the given email, username and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have an username')
        user = self.model(
            email = self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        """
        Creates and saves a superuser with the given email, username and password.
        """
        user = self.create_user(
            email = self.normalize_email(email), 
            username=username, 
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_user_to_follow(self, pk):
        users = User.objects.all().exclude(pk=pk)
        my_user = User.objects.get(pk=pk)
        avail = [user for user in users if user not in my_user.get_following()]
        return avail
    
    def get_mutual_followings(self, pk, other_pk):
        my_user = User.objects.get(pk=pk)
        my_follow = my_user.get_following()
        
        other_user = User.objects.get(pk=other_pk)
        other_user_follow = other_user.get_following()

        mutuals_list = list(my_follow.intersection(other_user_follow))
        mutuals_count = len(mutuals_list)
        return mutuals_count
    
def get_profile_image(instance, filename):
    upload_to = '{}/{}/{}'.format('user', instance.pk, 'profile')
    ext = filename.split('.')[-1]
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        filename = '{}_{}.{}'.format(instance.pk, uuid4().hex, ext)
    return os.path.join(upload_to, filename)

def get_default_profile_image():
    return "user/avatar.png"

def get_cover_image(instance, filename):
    upload_to = '{}/{}/{}'.format('user', instance.pk, 'cover')
    ext = filename.split('.')[-1]
    if instance.pk:
        filename = '{}_{}.{}'.format(instance.pk, 'cover', ext)
    else:
        filename = '{}_{}.{}'.format(instance.pk, uuid4().hex, ext)
    return os.path.join(upload_to, filename)

def get_default_cover_image():
    return "user/cover.jpg"

class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address', max_length=40, unique=True)
    username = models.CharField(max_length=30, primary_key=True, unique=True, verbose_name='username')
    bio = models.TextField(blank=True, null=True)
    follower = models.ManyToManyField("User", blank=True, related_name='followers') # people following profile
    following = models.ManyToManyField("User", blank=True, related_name='followings') # people profile is following 
    cover_pic = models.ImageField(upload_to=get_cover_image, default=get_default_cover_image, blank=True, null=True, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    profile_pic = models.ImageField(upload_to=get_profile_image, default=get_default_profile_image, blank=True, null=True, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    hide_email = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.profile_pic.path)
        if img.height > 250 or img.width > 250:
            size = (250, 250)
            img.thumbnail(size)
            img.save(self.profile_pic.path)
            
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def get_all_permissions(self=None):
        if self.is_admin:
            return set()

    def get_follower(self):
        return self.follower.all()

    def get_follower_no(self):
        return self.follower.count()

    def get_following(self):
        return self.following.all()

    def get_followering_no(self):
        return self.following.count()
    
