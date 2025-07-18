from ast import mod
from django.db import models
import datetime
import os
from django.core.validators import FileExtensionValidator
from uuid import uuid4
from django.urls import reverse
from django.utils.safestring import mark_safe
from user.models import User

def get_post_image(instance, filename):
    upload_to = '{}/{}/{}'.format('user', instance.post.user, 'post')
    ext = filename.split('.')[-1]
    date = instance.post.created_at.strftime('%Y%m%d')
    filename = '{}_{}_{}.{}'.format(instance.post.user, '_', date, ext)
    return os.path.join(upload_to, filename)

def get_repost_image(instance, filename):
    upload_to = '{}/{}/{}'.format('user', instance.post.user, 'repost')
    ext = filename.split('.')[-1]
    date = instance.post.created_at.strftime('%Y%m%d')
    filename = '{}_{}_{}.{}'.format(instance.post.user, '_', date, ext)
    return os.path.join(upload_to, filename)

class Tag(models.Model):
    tag = models.CharField(max_length=20, primary_key=True)

class Post(models.Model):
    user = models.ForeignKey(User, related_name="user_post", on_delete=models.CASCADE)
    caption = models.TextField(max_length=1500, blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='post_like', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    likes_num = models.PositiveIntegerField(default=0)
    views = models.IntegerField(default=0)
    repost = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reposts')

    def is_repost(self):
        return self.repost is not None
    
    def __str__(self):
        return f"{self.pk} - {self.caption[0:20]} by {self.user}"
    
    class Meta:
        ordering = ('-created_at',)

    def likes_no(self):
        likes = self.likes.count()
        likes_num = likes
        return likes_num
    
    def comment_no(self):
        return self.comment_post.count() # type: ignore
    
class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_images')
    image = models.ImageField(upload_to=get_post_image, blank=True, null=True, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])

    def image_tag(self):
        return mark_safe('<img src="/../../media/%s" width="100" height="100" />' % (self.image))

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_post')
    comment = models.CharField(max_length=700)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.user} commented {self.post} -- {self.comment[0:20]}"

    def save(self, *args, **kwargs):
        self.created_at = datetime.datetime.now()
        super(Comment, self).save(*args, **kwargs)

class BookMark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bookmarks')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    added = models.DateTimeField(auto_now_add=True)            