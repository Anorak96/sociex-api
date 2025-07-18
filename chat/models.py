from django.db import models
import os
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from user.models import User

def get_message_image(instance, filename):
    upload_to = '{}/{}/{}_{}'.format('message', instance.sender, 'to', instance.chat.receiver)
    ext = filename.split('.')[-1]
    filename = '{}_{}.{}'.format('message', instance.sender, ext)
    return os.path.join(upload_to, filename)

class Chat(models.Model):
    sender_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sender')
    receiver_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_receiver')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        unique_together = ('sender_user', 'receiver_user')

    def get_chat_group(self):
        return f"chat_{self.id}"

    def __str__(self):
        return f"{self.sender_user} - {self.receiver_user}"

class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="chat_messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to=get_message_image, blank=True, null=True, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    sent = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} sent {self.body}"