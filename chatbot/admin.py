
from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):  # or admin.StackedInline for bigger view
    model = Message
    extra = 1   # how many empty rows to show for adding new messages

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at')
    inlines = [MessageInline]   # show messages inside conversation

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'content', 'timestamp')
