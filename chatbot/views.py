import openai
from openai import OpenAI
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required
from .models import Conversation, Message
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.urls import reverse
client = OpenAI()

def home_view(request):
    return render(request, "chatbot/home.html")

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "chatbot/signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "chatbot/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def conversation_list(request):
    conversations = Conversation.objects.filter(user=request.user).order_by("-created_at")

    if request.headers.get("HX-Request"):
        return render(request, "chatbot/conversation_list_partial.html", {"conversations": conversations})

    if conversations.exists():
        return redirect("conversation_detail", conversation_id=conversations.first().id)
    else:
        return redirect("new_conversation")

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    messages = conversation.messages.all()

    if request.method == "POST":
        content = request.POST.get("content")
        if content.strip():
            
            Message.objects.create(
                conversation=conversation,
                role="user",
                content=content
            )

            chat_history = [{"role": msg.role, "content": msg.content} for msg in messages]
            chat_history.append({"role": "user", "content": content})

            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=chat_history,
                temperature=0.7
            )

            assistant_reply = response.choices[0].message.content.strip()

            Message.objects.create(
                conversation=conversation,
                role="assistant",
                content=assistant_reply
            )

            try:
                title_resp = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Summarize the chat in 5 words or fewer."},
                        {"role": "user", "content": "\n".join(m.content for m in conversation.messages.all()[:5])}
                    ]
                )
                new_title = title_resp.choices[0].message.content.strip()
                if new_title:
                    conversation.title = new_title
                    conversation.save()
            except Exception as e:
                print("Title rename failed:", e)

            if request.headers.get("Hx-Request"):  
                conversations = Conversation.objects.filter(user=request.user).order_by("-created_at")
                sidebar_html = render_to_string("chatbot/conversation_list_partial.html", {"conversations": conversations}, request=request)
                return HttpResponse(sidebar_html)

        return redirect("conversation_detail", conversation_id=conversation.id)

    return render(request, "chatbot/conversation_detail.html", {
        "conversation": conversation,
        "messages": messages
    })

@login_required
def new_conversation(request):

    conversation = Conversation.objects.create(
        user=request.user,
        title=f"Conversation {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    return redirect('conversation_detail', conversation_id=conversation.id)

from django.http import HttpResponse

@login_required
@require_POST
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
    conversation.delete()

    current_path = request.headers.get("HX-Current-URL", "")
    if str(conversation_id) in current_path:
        
        response = HttpResponse()
        response["HX-Redirect"] = reverse("new_conversation")
        return response

    if request.headers.get("HX-Request"):
        conversations = Conversation.objects.filter(user=request.user).order_by("-created_at")
        return render(request, "chatbot/conversation_list_partial.html", {"conversations": conversations})

    return redirect("new_conversation")
