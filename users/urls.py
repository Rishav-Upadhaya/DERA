from django.urls import path
from . import views
from .views import *
from property.views import userchat
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', Homepage.as_view(), name='homepage'),
    path('homepage', Homepage.as_view(), name='homepage'),
    path('login', CustomLoginView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('<str:username>', UserView.as_view(), name='user_view'),
    path('userdashboard/<int:userid>', views.userdashboard, name='userdashboard'),
    path('search/', views.search, name= 'search'),
    path('message/', views.message, name= 'message'),
    path('book_req/<int:propid>', views.book_req, name= 'book_req'),
    path('chat/<int:request_id>/messages/', views.get_chat_messages, name='chat_messages'),
    path('userchat/', userchat, name='userchat'),
]
