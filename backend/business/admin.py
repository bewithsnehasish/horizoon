from django.contrib import admin
from .models import Vehicle, Order

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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ['client__username', 'vehicle__vehicle_number']
    list_filter = ['payment_status', 'order_status', 'pickup_datetime', 'return_datetime']
    date_hierarchy = 'pickup_datetime'

    list_display = [
        'id',
        'client',
        'vehicle',
        'pickup_datetime',
        'return_datetime',
        'order_status',
        'payment_status',
        'rental_amount',
        'late_fee',
        'created_at',
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Client & Vehicle Info', {
            'fields': ('client', 'vehicle'),
        }),
        ('Rental Timing', {
            'fields': ('pickup_datetime', 'return_datetime', 'actual_return_datetime'),
        }),
        ('Location Details', {
            'fields': ('pickup_location', 'dropoff_location'),
        }),
        ('Payment Info', {
            'fields': ('rental_amount', 'security_deposit', 'late_fee', 'payment_status'),
        }),
        ('Status Tracking', {
            'fields': ('order_status', 'notes'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
