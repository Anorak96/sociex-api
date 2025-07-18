from rest_framework import serializers
from chat.models import Chat, ChatMessage
from user.serializers import UserSerializer
from django.utils.timesince import timesince
from datetime import datetime, timedelta
from django.utils import timezone
from user.models import User

class ChatMessageSerializer(serializers.ModelSerializer):
	sender = UserSerializer()
	sent = serializers.SerializerMethodField()

	def get_sent(self, obj):
		now = timezone.now()
		delta = now - obj.sent
		
		if delta < timedelta(days=1):
			return timesince(obj.sent) + ' ago'
		else:
			return obj.sent.strftime('%b %d, %Y %I:%M %p')

	class Meta:
		model = ChatMessage
		fields = ('id', 'chat', 'sender', 'body', 'image', 'sent', 'read')

class ChatSerializer(serializers.ModelSerializer):	
	dm_messages = serializers.SerializerMethodField()
	sender_user = UserSerializer()
	receiver_user = UserSerializer()
	created = serializers.SerializerMethodField()

	def get_created(self, obj):
		now = timezone.now()
		delta = now - obj.created
		
		if delta < timedelta(days=1):
			return timesince(obj.created) + ' ago'
		else:
			return obj.created.strftime('%b %d, %Y %I:%M %p')

	def get_dm_messages(self, obj):
		messages = ChatMessage.objects.filter(chat=obj)
		if messages:
			return ChatMessageSerializer(messages, many=True).data

	class Meta:
		model = Chat
		fields = ('id', 'sender_user', 'receiver_user', 'created', 'dm_messages')

class CreateMessageSerializer(serializers.ModelSerializer):
	chat = serializers.IntegerField()
	body = serializers.CharField()
	image = serializers.ImageField(required=False, allow_null=True, write_only=True)
	
	class Meta:
		model = ChatMessage
		fields = ['chat', 'body', 'image']
		
	def create(self, validated_data):
		sender = self.context['request'].use
		chat_ = Chat.objects.get(id=validated_data['chat'])
		
		message = ChatMessage.objects.create(
            chat = chat_,
            body = validated_data['body'],
            sender = sender,
			image = validated_data['image']
        )
		message.save