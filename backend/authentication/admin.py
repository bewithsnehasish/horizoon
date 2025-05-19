from django.contrib import admin

from authentication.models import  Client, ClientDetails

# Register your models here.

admin.site.register(Client)
admin.site.register(ClientDetails)
