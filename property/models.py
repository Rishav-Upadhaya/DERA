from django.db import models
# from users.models import User
from django.contrib.auth.models import User
# Create your models here.

class property(models.Model):
    owner = models.ForeignKey(User, on_delete= models.CASCADE, related_name="owner")
    property_img = models.ImageField(upload_to="images/")
    description = models.TextField()
    price = models.IntegerField()
    location = models.CharField(max_length=100)
    published_at = models.DateTimeField(auto_now_add=True)

    def __self__(self):
        return self.description
    
class BookReq(models.Model):
    booker = models.ForeignKey(User, on_delete=models.CASCADE)
    properid = models.ForeignKey(property, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booker} requested {self.properid}"

class BookReqStatus(models.Model):
    bookreqid = models.ForeignKey(BookReq, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    reqanstime = models.DateTimeField(auto_now_add=True)

# class Facilities(models.Model):
#     id = models.ForeignKey(property, on_delete=models.CASCADE, related_name="property_id")
#     parking = models.BooleanField()
#     water = models.BooleanField()
#     area = models.IntegerField()
#     sunlight = models.BooleanField()

class Favourites(models.Model):
    favowner = models.ForeignKey(User, on_delete= models.CASCADE, related_name="favowner")
    favproperid = models.ForeignKey(property, on_delete= models.CASCADE, related_name="favproperid")
    is_favourite = models.BooleanField(default=True)

class ChatMessage(models.Model):
    book_request = models.ForeignKey(BookReq, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} in {self.book_request}"
