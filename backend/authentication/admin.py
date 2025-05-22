from django.contrib import admin
from authentication.models import Renter, Client, ClientDetails


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    search_fields = ['username', 'email', 'authToken']
    list_filter = ['createdAt']
    date_hierarchy = 'createdAt'
    list_display = ['username', 'email', 'createdAt', 'authToken']
    readonly_fields = ['user_id', 'authToken', 'createdAt', 'updatedAt']


@admin.register(ClientDetails)
class ClientDetailsAdmin(admin.ModelAdmin):  
    search_fields = ['name', 'phone', 'aadhaar']
    list_filter = ['gender', 'joinedAt']
    date_hierarchy = 'joinedAt'
    list_display = ['name', 'phone', 'gender', 'age', 'aadhaar', 'joinedAt']
    readonly_fields = ['joinedAt']


@admin.register(Renter)
class RenterAdmin(admin.ModelAdmin):
    
    search_fields = ['full_name', 'email', 'aadhaar', 'phone']
    list_filter = ['gender', 'verification_status', 'joinedAt']
    date_hierarchy = 'joinedAt'
    list_display = [
        'full_name',
        'email',
        'phone',
        'gender',
        'rating',
        'verification_status',
        'joinedAt',
        'addedby',
    ]
    readonly_fields = ['user_id', 'joinedAt']
