from .models import Conversation

def user_conversations(request):
    if request.user.is_authenticated:
        conversations = Conversation.objects.filter(user=request.user)
    else:
        conversations = []
    return {"conversations": conversations}
