# from django.contrib import admin
# from .models import User, userForm

# Register your models here.
# admin.site.register(userForm)
from django.contrib import admin
from .models import *

admin.site.register(Message)
# from .models import UserProfile

# # admin.site.register(UserProfile)


# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ("user", "citizenship")

# admin.site.register(UserProfile, UserProfileAdmin)

