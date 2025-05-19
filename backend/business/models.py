from django.db import models
from authentication.models import Renter

import uuid


class Vehicle(models.Model):
    class TransmissionChoices(models.TextChoices):
        MANUAL = "Manual"
        AUTOMATIC = "Automatic"

    class FuelChoices(models.TextChoices):
        PETROL = "Petrol"
        DIESEL = "Diesel"
        ELECTRIC = "Electric"
        CNG = "CNG"

    class VehicleTypeChoices(models.TextChoices):
        CAR = "Car"
        BIKE = "Bike"
        SUV = "SUV"
        SCOOTER = "Scooter"
        TRUCK = "Truck"
        OTHER = "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=20, choices=VehicleTypeChoices.choices)
    transmission = models.CharField(max_length=10, choices=TransmissionChoices.choices)
    fuel_type = models.CharField(max_length=10, choices=FuelChoices.choices)
    seating_capacity = models.PositiveIntegerField()
    mileage = models.FloatField(help_text="km per liter or km per charge")
    engine_cc = models.PositiveIntegerField(null=True, blank=True)
    color = models.CharField(max_length=30)
    top_speed = models.PositiveIntegerField(null=True, blank=True, help_text="in km/h")
    location = models.TextField()
    current_odometer = models.FloatField(help_text="in kilometers")
    insurance_expiry_date = models.DateField()

    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
    late_fee_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    image_1 = models.TextField()
    image_2 = models.TextField()
    image_3 = models.TextField()
    

    
    added_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    rating = models.FloatField(default=0.0)
    total_trips = models.PositiveIntegerField(default=0)

    
    owner = models.ForeignKey(Renter, on_delete=models.SET_NULL, null=True, blank=True)

    STATUS_CHOICES = [
        ("available", "Available"),
        ("booked", "Booked")
    ]
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")

    def __str__(self):
        return f"{self.name} ({self.vehicle_number})"



# class Order(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

#     client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
#     vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='orders')


#     # Rental timing
#     pickup_datetime = models.DateTimeField()
#     return_datetime = models.DateTimeField()

#     actual_return_datetime = models.DateTimeField(null=True, blank=True)  # if returned late

#     pickup_location = models.TextField()
#     dropoff_location = models.TextField()

#     rental_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     security_deposit = models.DecimalField(max_digits=10, decimal_places=2)
#     late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    

#     payment_status = models.CharField(
#         max_length=20,
#         choices=[
#             ('pending', 'Pending'),
#             ('paid', 'Paid'),
#             ('failed', 'Failed'),
#             ('refunded', 'Refunded')
#         ],
#         default='pending'
#     )

#     order_status = models.CharField(
#         max_length=20,
#         choices=[
#             ('upcoming', 'Upcoming'),
#             ('ongoing', 'Ongoing'),
#             ('completed', 'Completed'),
#             ('cancelled', 'Cancelled')
#         ],
#         default='upcoming'
#     )

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     notes = models.TextField(blank=True)

#     def __str__(self):
#         return f"Order {self.id} | {self.client.username} -> {self.vehicle.name}"

#     class Meta:
#         ordering = ['-created_at']
