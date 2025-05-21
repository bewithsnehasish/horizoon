# business/serializers.py
from rest_framework import serializers

from business.models import Order, Vehicle


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "vehicle",
            "pickup_datetime",
            "return_datetime",
            "actual_return_datetime",
            "pickup_location",
            "dropoff_location",
            "rental_amount",
            "security_deposit",
            "late_fee",
            "payment_status",
            "order_status",
            "created_at",
            "otp",
        ]
        depth = 1  # Show nested vehicle details


class CreateOrderSerializer(serializers.ModelSerializer):
    vehicle_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Order
        fields = [
            "vehicle_id",
            "pickup_datetime",
            "return_datetime",
            "pickup_location",
            "dropoff_location",
        ]

    def validate(self, attrs):
        # Add custom validation here
        if attrs["return_datetime"] <= attrs["pickup_datetime"]:
            raise serializers.ValidationError(
                "Return datetime must be after pickup datetime"
            )

        # Get the vehicle instance
        try:
            vehicle = Vehicle.objects.get(id=attrs["vehicle_id"])
        except Exception:
            raise serializers.ValidationError("Invalid vehicle_id, Vehicle not found")

        # Add vehicle to validated data
        attrs["vehicle"] = vehicle
        return attrs
