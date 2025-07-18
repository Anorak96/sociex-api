from django.contrib import admin
from .models import Chat, ChatMessage

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 3

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender_user', 'receiver_user', 'created')
    fieldsets = (
        (None, {
            "fields": ('sender_user', 'receiver_user'),
        }),
    )
    list_filter = ('sender_user', 'receiver_user', 'created')
    readonly_fields = ('created',)
    ordering = ('-created',)
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'body', 'chat', 'read', 'sent')
    list_filter = ('sender', 'chat')
    readonly_fields = ('sent',)
    ordering = ('-sent',)