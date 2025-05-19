from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    search_fields = ['vehicle_number', 'name', 'brand', 'model', 'location']
    list_filter = [
        'vehicle_type',
        'transmission',
        'fuel_type',
        'current_status',
        'added_on',
    ]
    date_hierarchy = 'added_on'
    
    list_display = [
        'vehicle_number',
        'name',
        'brand',
        'model',
        'vehicle_type',
        'transmission',
        'fuel_type',
        'current_status',
        'price_per_day',
        'rating',
        'total_trips',
        'owner',
        'added_on',
    ]

    readonly_fields = ['added_on', 'last_updated']

    fieldsets = (
        ('Basic Info', {
            'fields': ('vehicle_number', 'name', 'brand', 'model', 'vehicle_type', 'color')
        }),
        ('Technical Specs', {
            'fields': ('transmission', 'fuel_type', 'seating_capacity', 'mileage', 'engine_cc', 'top_speed', 'current_odometer')
        }),
        ('Pricing & Status', {
            'fields': ('price_per_hour', 'price_per_day', 'security_deposit', 'late_fee_per_hour', 'current_status')
        }),
        ('Owner & Dates', {
            'fields': ('owner', 'insurance_expiry_date', 'added_on', 'last_updated')
        }),
        ('Images', {
            'fields': ('image_1', 'image_2', 'image_3')
        }),
        ('Stats', {
            'fields': ('rating', 'total_trips')
        }),
        ('Location', {
            'fields': ('location',)
        }),
    )
