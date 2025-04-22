import json, os
from django.shortcuts import render
# from users.models import User
from django.contrib.auth.models import User
from .forms import PropertyForm
from .models import property, BookReq, Favourites, BookReqStatus, ChatMessage
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from openai import OpenAI
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.views.decorators.http import require_POST
import requests

API_KEY = os.getenv('DEEPSEEK_API_KEY')

# Create your views here.
# @login_required
# def addProperty(request):
#     form = PropertyForm()
#     if request.method == "POST":  
#         print('0000')  
#         form = PropertyForm(request.POST, request.FILES)
#         if form.is_valid():
#             print('00000')
#             property_instance = form.save(commit=False)  # Don't save yet
#             property_instance.owner = request.user  # Assign logged-in user
#             property_instance.location = property_instance.location.lower()
#             property_instance.description = property_instance.description.lower()
#             property_instance.save()
#             return HttpResponseRedirect(reverse('user_view', kwargs={'username': request.user.username}))
#         else:
#             print(form.errors)

#     return render(request, 'property/addproperty.html',{
#         'form': form
#     })

class AddPropertyView(LoginRequiredMixin, generic.CreateView):
    model = property
    form_class = PropertyForm
    template_name = 'property/addproperty.html'
    
    def form_valid(self, form):
        property_instance = form.save(commit=False)
        property_instance.owner = self.request.user
        property_instance.location = property_instance.location.lower()
        property_instance.description = property_instance.description.lower()
        property_instance.save()
        return HttpResponseRedirect(reverse('user_view', kwargs={'username': self.request.user.username}))


def viewproperty(request, propid):
    prop = property.objects.get(pk = propid)
    favs = Favourites.objects.filter(favowner=request.user)
    fav_property_ids = favs.values_list('favproperid', flat=True)
    return render(request, "property/properties.html", {'prop': prop, 'favdata' : fav_property_ids})


@login_required
def userprop(request, userprop):
    # Ensure the current user is authenticated
    current_user = request.user

    # Retrieve all favorite entries for the current user
    favs = Favourites.objects.filter(favowner=current_user)

    # Extract the property IDs from the favorites
    fav_property_ids = favs.values_list('favproperid', flat=True)

    # Retrieve the properties corresponding to the favorite IDs
    favorite_properties = property.objects.filter(id__in=fav_property_ids)

    return render(request, "property/yourFavourites.html", {'properties': favorite_properties, 'favdata': fav_property_ids})


# def chatAI(content):
#     client = OpenAI(
#         base_url="https://openrouter.ai/api/v1",
#         api_key=API_KEY
#     )

#     chat = client.chat.completions.create(
#         model= "deepseek/deepseek-r1:free",
#         messages=[
#             {
#             "role":"user",
#             "content": content,
#             }
#         ]
#     )
#     return chat.choices[0].message.content

def chatAI(content):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=API_KEY,
        timeout=60
    )

    def stream_response():
        try:
            properties_data = list(property.objects.values('description', 'location', 'price'))
            
            response = client.chat.completions.create(
                model="deepseek/deepseek-r1:free",
                messages=[
                    {"role": "system", "content": """You are a helpful assistant for a property rental platform. 
                    Format your responses in a clean, readable way:
                    
                    1. Use simple line breaks to separate sections
                    2. Use numbers or simple dashes for lists
                    3. Keep important details like prices, locations, and key features on separate lines
                    4. Use spacing to make the text easy to read
                    5. Don't use any markdown, special characters, or formatting symbols
                    
                    Example format:
                    For Normal chats:-
                    be calm confident and give the precise answer.
                     - Answer.

                    For property related chats:- 
                    
                    Property Recommendation:
                    
                    1. Location Name (Type, Price)
                    Location: Details
                    Features:
                    - Feature 1
                    - Feature 2
                    
                    Commute Info:
                    - Distance details
                    - Transport options
                    
                    Here are the available properties: """ + json.dumps(properties_data)},
                    {"role": "user", "content": content}
                ],
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    # Clean the text while preserving line breaks
                    clean_text = chunk.choices[0].delta.content.replace('*', '').replace('#', '').replace('_', '')
                    yield f"data: {json.dumps({'message': clean_text})}\n\n"
            
            yield "data: {\"message\": \"\\n\"}\n\n"
            yield "event: Done\ndata: [DONE]\n\n"
        except Exception as e:
            error_message = str(e)
            print(f"Error in chatAI: {error_message}")
            yield f"data: {json.dumps({'error': error_message})}\n\n"

    response = StreamingHttpResponse(stream_response(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response

@csrf_exempt
def userchat(request):
    if request.method == "GET":
        question = request.GET.get("askgpt")
        if question:
            return chatAI(question)
    return HttpResponse(status=400)


def book_request(request, userName):
    # Get property objects for this user
    user_properties = property.objects.filter(owner=userName)
    
    # Get all BookReq objects for these properties
    book_requests = BookReq.objects.filter(properid__in=user_properties).select_related('properid', 'booker')
    
    # Get unique property IDs from book requests
    property_ids = book_requests.values_list('properid', flat=True).distinct()
    
    # Get the properties that have book requests
    room_cards = property.objects.filter(pk__in=property_ids)
    
    print(f"Found {len(room_cards)} properties with requests")
    print(f"Found {len(book_requests)} book requests")
    
    # Group messages by property
    messages_by_property = {}
    for req in book_requests:
        if req.properid_id not in messages_by_property:
            messages_by_property[req.properid_id] = []
        messages_by_property[req.properid_id].append(req)
    
    return render(request, "property/book_request.html", {
        "room_cards": room_cards,
        "messages": book_requests,
        "messages_by_property": messages_by_property
    })

def favourites(request, fid):
    # fid is the property Id
    currentuser = request.user
    propertid = property.objects.get(pk = fid)
    favorite, created = Favourites.objects.get_or_create(
        favowner=request.user,
        favproperid=propertid
    )
    if not created:
        # If the favorite already exists, delete it (unfavorite)
        favorite.delete()
        # Optionally, add a message indicating the property was removed from favorites
    else:
        # Optionally, add a message indicating the property was added to favorites
        pass
    return HttpResponseRedirect(reverse('user_view', kwargs={'username': request.user.username}))

class DelPropertyView(generic.DeleteView):
    model = property
    template_name = 'property/delete_property.html'
    
    def get_success_url(self):
        return reverse('user_view', kwargs={'username': self.request.user.username})
    
    def dispatch(self, request, *args, **kwargs):
        # Check if the user is the owner of the property
        obj = self.get_object()
        if obj.owner != request.user:
            return HttpResponseRedirect(reverse('user_view', kwargs={'username': request.user.username}))
        return super().dispatch(request, *args, **kwargs)


@csrf_exempt
def bookreqstatus(request, pk, typestatus):
    if request.method == "POST":
        try:
            print(f"Processing request for BookReq ID: {pk}")
            book_request = BookReq.objects.get(pk=pk)
            print(f"Found book request: {book_request}")
            
            # Create the status record
            status = BookReqStatus.objects.create(
                bookreqid=book_request,
                is_accepted=(typestatus == 'accepted'),
                is_rejected=(typestatus == 'rejected')
            )
            print(f"Created status record: {status}")
            
            # Update the book request status
            book_request.status = typestatus
            book_request.save()
            print("Updated book request status")
            
            # Return success response with redirect URL
            return JsonResponse({
                'status': 'success',
                'redirect_url': reverse('message')
            })
            
        except BookReq.DoesNotExist:
            print(f"BookReq with ID {pk} not found")
            return JsonResponse({
                'status': 'error',
                'message': 'Book request not found'
            }, status=404)
        except Exception as e:
            print(f"Error in bookreqstatus: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

@require_POST
@csrf_exempt
def send_message(request, request_id):
    try:
        data = json.loads(request.body)
        message_text = data.get('message')
        book_request = BookReq.objects.get(pk=request_id)
        
        # Verify user is part of this conversation
        if request.user != book_request.booker and request.user != book_request.properid.owner:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Create new message
        message = ChatMessage.objects.create(
            book_request=book_request,
            sender=request.user,
            message=message_text
        )
        
        return JsonResponse({
            'id': message.id,
            'message': message.message,
            'sender': message.sender.username,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    except BookReq.DoesNotExist:
        return JsonResponse({'error': 'Chat not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_chat_messages(request, request_id):
    try:
        book_request = BookReq.objects.get(pk=request_id)
        
        # Verify user is part of this conversation
        if request.user != book_request.booker and request.user != book_request.properid.owner:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        messages = ChatMessage.objects.filter(book_request=book_request)
        
        return JsonResponse({
            'messages': [{
                'id': msg.id,
                'message': msg.message,
                'sender': msg.sender.username,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            } for msg in messages]
        })
    except BookReq.DoesNotExist:
        return JsonResponse({'error': 'Chat not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)