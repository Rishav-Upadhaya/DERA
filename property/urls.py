from django.urls import path
from . import views
from .views import *
from django.views.generic.base import RedirectView

urlpatterns = [
    path('bookreqstatus/<int:pk>/<str:typestatus>/', views.bookreqstatus, name="bookreqstatus"),
    path('chat/<int:request_id>/messages/', views.get_chat_messages, name='get_chat_messages'),
    path('chat/<int:request_id>/send/', views.send_message, name='send_message'),
    path('addProperty', AddPropertyView.as_view(), name="addProperty"),
    path('bookRequest/<int:userName>', views.book_request, name="bookRequest"),    
    path('favourite/<int:fid>', views.favourites, name="favourite"),    
    path('delete/<int:pk>/', views.DelPropertyView.as_view(), name='delete'),
    path('userchat/', views.userchat, name="userchat"),    
    path('chat/', views.userchat, name='chat'),
    path('<int:propid>', views.viewproperty, name="viewproperty"),    
    path('<str:userprop>', views.userprop, name="userprop"),    
]
