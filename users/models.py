from django.db import models
from django.contrib.auth.models import User
from property.models import BookReq

class Message(models.Model):
    request = models.ForeignKey(BookReq, on_delete=models.CASCADE, related_name='messagesreq')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'users_message'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['request', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.sender.username} - {self.timestamp}"
