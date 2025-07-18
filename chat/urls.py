from django.urls import path
from . import views

app_name = 'chat_api'
urlpatterns = [
    path('chats', views.ChatsView.as_view(), name='chats'),
    path('chat/<int:id>', views.ChatView.as_view(), name='chat'),
]
