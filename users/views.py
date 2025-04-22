from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, StreamingHttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views import View
from property.models import property, BookReq, Favourites
from django.views.generic import ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Message
from django.utils import timezone
import json
import requests
from property.views import userchat as property_userchat

# Create your views here.

class Homepage(ListView):
    model = property
    template_name = "users/homepage.html"
    context_object_name = "property_data"


class CustomLoginView(View):
    template_name = "users/login.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password1")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("user_view", username.capitalize())
        else:
            return render(request, self.template_name, {
                "message": "Invalid Credentials."
            })


def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.save()
            login(request, user)
            return render(request, "users/login.html")
        else:
            print(form.errors)
            return redirect('register')

    return render(request, "users/register.html", {'form': form})

def logout_view(request):
    logout(request)
    return render(request, "users/login.html",{
        "message":"Logged Out Successfully."
    })

class UserView(LoginRequiredMixin, TemplateView):
    template_name = "users/home.html"
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get('q', '')
        if q:
            room_cards = property.objects.filter(location__icontains=q)
        else:
            room_cards = property.objects.all()
        favs = Favourites.objects.filter(favowner=self.request.user)
        fav_property_ids = favs.values_list('favproperid', flat=True)
        
        context['room_cards'] = room_cards
        context['favdata'] = fav_property_ids
        return context

def userdashboard(request, userid):
    print(userid)
    if User.is_authenticated:
        user = User.objects.get(pk = userid)
        userprop = [prop for prop in property.objects.filter(owner = user)]
        
        return render(request, "users/userdashboard.html", {'userinfo': user, 'userprop': userprop})

def search(request):
    if request.method == "POST":
        searchtxt = request.POST.get("search-input").strip()
        propid = property.objects.filter(location = searchtxt)
        url = reverse('user_view', kwargs={'username': request.user.username})
        return redirect(f"{url}?q={searchtxt}")
    else:
        propid = property.objects.all()
        return render(request, "users/home.html", {'room_cards':propid})
    

def message(request):
    accepted_requests = BookReq.objects.filter(
        status='accepted'
    ).filter(
        Q(booker=request.user) | Q(properid__owner=request.user)
    ).select_related('properid', 'properid__owner', 'booker')

    messages = []
    if accepted_requests.exists():
        first_request = accepted_requests.first()
        messages = Message.objects.filter(request=first_request).select_related('sender').order_by('timestamp')

    return render(request, "users/message.html", {
        'accepted_requests': accepted_requests,
        'messages': messages
    })

def book_req(request, propid):
    print("000")
    if request.method == "POST":
        print("000")
        message1 = request.POST["requestMessage"]
        proper = property.objects.get(pk = propid)
        print(f"{request.user} has a message {message1} for property of id {propid}")
        BookReq.objects.create(booker = request.user , properid = proper, message = message1)
        return HttpResponseRedirect(reverse('user_view', kwargs={'username': request.user.username}))
    
    return HttpResponseRedirect(reverse('user_view', kwargs={'username': request.user.username}))

def get_chat_messages(request, request_id):
    try:
        book_request = BookReq.objects.get(id=request_id)
        if request.user != book_request.booker and request.user != book_request.properid.owner:
            return JsonResponse({'error': 'Access denied'}, status=403)

        messages = Message.objects.filter(
            request=book_request
        ).select_related('sender').order_by('timestamp')

        messages_data = []
        for msg in messages:
            messages_data.append({
                'message': msg.content,
                'sender': msg.sender.username,
                'timestamp': msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'is_outgoing': msg.sender == request.user
            })
        
        return JsonResponse({
            'messages': messages_data,
            'status': 'success'
        })
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def userchat(request):
    """Handle DeepSeek chatbot messages by forwarding to property.views.userchat"""
    try:
        return property_userchat(request)
    except Exception as e:
        print(f"Error in chatbot: {e}")
        return JsonResponse({
            'error': str(e),
            'message': 'Sorry, I encountered an error. Please try again.',
            'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        }, status=500)
