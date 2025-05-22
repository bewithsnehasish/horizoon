import uuid

from django.db import models

from authentication.models import Client, Renter


class Vehicle(models.Model):
    """
    Represents a Vehicle on the Platform
    """
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

    vehicle_number = models.CharField(
        max_length=15,
        unique=True,
        help_text="Unique registration number of the vehicle."
    )
    name = models.CharField(max_length=100, help_text="Vehicle name or title.")
    brand = models.CharField(max_length=50, help_text="Brand or manufacturer of the vehicle.")
    model = models.CharField(max_length=50, help_text="Model variant of the vehicle.")
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleTypeChoices.choices,
        help_text="Type/category of the vehicle."
    )
    transmission = models.CharField(
        max_length=10,
        choices=TransmissionChoices.choices,
        help_text="Transmission type (Manual or Automatic)."
    )
    fuel_type = models.CharField(
        max_length=10,
        choices=FuelChoices.choices,
        help_text="Fuel type used by the vehicle."
    )
    seating_capacity = models.PositiveIntegerField(help_text="Number of seats available.")
    mileage = models.FloatField(help_text="Mileage in km per liter or km per charge.")
    engine_cc = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Engine capacity in CC (optional)."
    )
    color = models.CharField(max_length=30, help_text="Color of the vehicle.")
    top_speed = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Top speed in km/h (optional)."
    )
    location = models.TextField(help_text="Current location of the vehicle.")
    current_odometer = models.FloatField(help_text="Current odometer reading in kilometers.")
    insurance_expiry_date = models.DateField(help_text="Insurance expiry date of the vehicle.")

    price_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Rental price per hour."
    )
    price_per_day = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Rental price per day."
    )
    security_deposit = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Refundable security deposit."
    )
    late_fee_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00,
        help_text="Fee charged per hour if the vehicle is returned late."
    )

    image_1 = models.TextField(help_text="Primary image of the vehicle.")
    image_2 = models.TextField(help_text="Secondary image of the vehicle.")
    image_3 = models.TextField(help_text="Tertiary image of the vehicle.")

    added_on = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the vehicle was added.")
    last_updated = models.DateTimeField(auto_now=True, help_text="Last updated timestamp.")
    rating = models.FloatField(default=0.0, help_text="Average customer rating.")
    total_trips = models.PositiveIntegerField(default=0, help_text="Total number of completed bookings.")

    owner = models.ForeignKey(
        Renter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Renter who owns this vehicle."
    )

    STATUS_CHOICES = [("available", "Available"), ("booked", "Booked")]
    current_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available",
        help_text="Current availability status of the vehicle."
    )

    def __str__(self):
        return f"{self.name} ({self.vehicle_number})"


class Order(models.Model):
    """
    Represents a Order on the Platform
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="orders",
        help_text="Client who placed this order."
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="orders",
        help_text="Vehicle associated with this order."
    )

    pickup_datetime = models.DateTimeField(help_text="Scheduled pickup date and time.")
    return_datetime = models.DateTimeField(help_text="Scheduled return date and time.")
    actual_return_datetime = models.DateTimeField(
        null=True, blank=True,
        help_text="Actual date and time when the vehicle was returned (optional)."
    )

    pickup_location = models.TextField(help_text="Pickup location for the vehicle.")
    dropoff_location = models.TextField(help_text="Drop-off location for the vehicle.")

    rental_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Total rental cost for the booking."
    )
    security_deposit = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Security deposit collected at the time of booking."
    )
    late_fee = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0.00,
        help_text="Late return penalty fee."
    )

    otp = models.CharField(
        max_length=6,
        null=True,
        blank=True,
        help_text="One-time passcode for verification during handover."
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("failed", "Failed"),
            ("refunded", "Refunded"),
        ],
        default="pending",
        help_text="Status of the payment for this order."
    )

    order_status = models.CharField(
        max_length=20,
        choices=[
            ("upcoming", "Upcoming"),
            ("ongoing", "Ongoing"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="upcoming",
        help_text="Current status of the order."
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the order was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the order was last updated.")

    notes = models.TextField(blank=True, help_text="Any additional notes or remarks.")

    def __str__(self):
        return f"Order {self.id} | {self.client.username} -> {self.vehicle.name}"

    class Meta:
        ordering = ["-created_at"]
