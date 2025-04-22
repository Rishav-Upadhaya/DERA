from django.contrib import admin
from .models import *

# Register your models here.
class propertyAdmin(admin.ModelAdmin):
    list_fields = ("owner", "description", "price","location", "published_at" )

class BookReqAdmin(admin.ModelAdmin):
    list_fields = ("booker","message", "published_at" )

class FavAdmin(admin.ModelAdmin):
    list_fields = (all)



admin.site.register(property, propertyAdmin)
admin.site.register(BookReq, BookReqAdmin)
admin.site.register(Favourites, FavAdmin)
# admin.site.register([all])

