from rest_framework.views import APIView
from chat.models import Chat
from rest_framework.response import Response
from . import serializers
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema
from django.db.models import Q

@extend_schema(tags=["Chat"])
class ChatsView(APIView):
	serializer_class = serializers.ChatSerializer
	permission_classes = [permissions.IsAuthenticated]
	
	def get(self, request):
		user = request.user
		chats = Chat.objects.filter(Q(sender_user=user) | Q(receiver_user=user))
		serializer = serializers.ChatSerializer(chats, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(tags=["Chat"])
class ChatView(APIView):
	serializer_class = serializers.ChatSerializer
	permission_classes = [permissions.IsAuthenticated]
	
	def get(self, request, id):
		chat = Chat.objects.get(id=id)
		serializer = serializers.ChatSerializer(chat)
		return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(tags=["Chat"])
class SendMessage(APIView):
    serializer_class = serializers.CreateMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = serializers.CreateMessageSerializer(data=request.data, context={'request': self.request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)