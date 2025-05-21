import json
import random
from datetime import datetime, timedelta

from django.db import connection
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import status

from authentication.models import Client
from business.models import Order, Vehicle
from business.serializers import CreateOrderSerializer, OrderSerializer


@csrf_exempt
def get_all_vehicles(request):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                id, name, brand, vehicle_type, location, 
                price_per_day, price_per_hour, image_1, 
                current_status, rating, seating_capacity 
            FROM business_vehicle
        """
        )
        columns = [col[0] for col in cursor.description]
        vehicles = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Convert Decimal/UUID to str/float if needed
        for v in vehicles:
            v["id"] = str(v["id"])
            v["price_per_day"] = float(v["price_per_day"])
            v["price_per_hour"] = float(v["price_per_hour"])
            v["rating"] = float(v["rating"])

    return JsonResponse({"vehicles": vehicles}, safe=False)


@csrf_exempt
@require_POST
def get_vehicle_details(request):
    try:
        body = json.loads(request.body)
        vehicle_id = body.get("vehicle_id")

        if not vehicle_id:
            return JsonResponse({"error": "vehicle_id is required"}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    v.id, v.vehicle_number, v.name, v.brand, v.model, v.vehicle_type, v.transmission, 
                    v.fuel_type, v.seating_capacity, v.mileage, v.engine_cc, v.color, v.top_speed, 
                    v.location, v.current_odometer, v.insurance_expiry_date,
                    v.price_per_day, v.price_per_hour, v.security_deposit, v.late_fee_per_hour,
                    v.image_1, v.image_2, v.image_3,
                    v.rating, v.total_trips, v.current_status,
                    r.user_id AS owner_id
                FROM business_vehicle v
                LEFT JOIN authentication_renter r ON v.owner_id = r.id
                WHERE v.id = %s
                LIMIT 1
            """,
                [vehicle_id],
            )

            row = cursor.fetchone()
            if not row:
                return JsonResponse({"error": "Vehicle not found"}, status=404)

            columns = [col[0] for col in cursor.description]
            vehicle = dict(zip(columns, row))

            # Type conversions
            vehicle["id"] = str(vehicle["id"])
            vehicle["owner_id"] = (
                str(vehicle["owner_id"]) if vehicle["owner_id"] else None
            )
            vehicle["price_per_day"] = float(vehicle["price_per_day"])
            vehicle["price_per_hour"] = float(vehicle["price_per_hour"])
            vehicle["security_deposit"] = float(vehicle["security_deposit"])
            vehicle["late_fee_per_hour"] = float(vehicle["late_fee_per_hour"])
            vehicle["rating"] = float(vehicle["rating"])
            vehicle["mileage"] = float(vehicle["mileage"])
            vehicle["current_odometer"] = float(vehicle["current_odometer"])
            vehicle["insurance_expiry_date"] = vehicle[
                "insurance_expiry_date"
            ].isoformat()

        return JsonResponse({"vehicle": vehicle})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def list_user_orders(request):
    """List all orders for the authenticated user"""
    try:
        data = json.loads(request.body)
        auth_token = data.get("authToken")
        if not auth_token:
            return JsonResponse({"error": "authToken is required"}, status=400)

        try:
            client = Client.objects.get(authToken=auth_token)
        except Exception:
            return JsonResponse({"error": "Invalid authentication token"}, status=401)

        orders = Order.objects.filter(client=client).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        # Need to convert serializer.data to JSON-serializable format
        orders_data = []
        for order in serializer.data:
            orders_data.append(order)
        return JsonResponse({"orders": orders_data}, safe=False)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def create_booking(request):
    """Create new booking with OTP verification"""
    try:
        data = json.loads(request.body)
        auth_token = data.get("authToken")
        print("Received data:", data)  # Debug what you're receiving

        vehicle_id = data.get("vehicle_id")
        print("Vehicle ID received:", vehicle_id, type(vehicle_id))  # Debug type

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)
            print("Found vehicle:", vehicle)  # Debug if found
        except Vehicle.DoesNotExist:
            print(f"No vehicle found with ID: {vehicle_id}")  # Debug
            return JsonResponse(
                {"error": f"Vehicle with ID {vehicle_id} not found"}, status=404
            )

        if not auth_token:
            return JsonResponse({"error": "authToken is required"}, status=400)
        if not vehicle_id:
            return JsonResponse({"error": "vehicle_id is required"}, status=400)

        try:
            client = Client.objects.get(authToken=auth_token)
            vehicle = Vehicle.objects.get(id=vehicle_id)  # Now vehicle_id is defined

            # Rest of your existing code...
            pickup = data.get("pickup_datetime")
            return_dt = data.get("return_datetime")

            if not all([pickup, return_dt]):
                return JsonResponse(
                    {"error": "Both pickup and return datetime are required"},
                    status=400,
                )

            # Check for overlapping bookings
            overlapping = Order.objects.filter(
                vehicle=vehicle,
                pickup_datetime__lt=return_dt,
                return_datetime__gt=pickup,
                order_status__in=["upcoming", "ongoing"],
            ).exists()

            if overlapping:
                return JsonResponse(
                    {"error": "Vehicle not available for selected dates"},
                    status=400,
                )

            # Create order
            serializer = CreateOrderSerializer(data=data)
            if serializer.is_valid():
                # Generate OTP (6-digit number)
                otp = str(random.randint(100000, 999999))

                order = serializer.save(
                    client=client,
                    vehicle=vehicle,
                    rental_amount=vehicle.price_per_day,
                    security_deposit=vehicle.security_deposit,
                    otp=otp,
                )

                print(f"OTP for order {order.id}: {otp}")  # For testing

                return JsonResponse(
                    {
                        "success": True,
                        "order_id": str(order.id),
                        "otp": otp,
                        "message": "Booking created successfully. Please verify with OTP.",
                    },
                    status=201,
                )
            return JsonResponse(serializer.errors, status=400)

        except Client.DoesNotExist:
            return JsonResponse({"error": "Invalid authToken"}, status=401)
        except Vehicle.DoesNotExist:
            return JsonResponse({"error": "Vehicle not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def check_availability(request):
    """Check vehicle availability for given dates"""
    try:
        data = json.loads(request.body)
        vehicle_id = data.get("vehicle_id")
        pickup = data.get("pickup_datetime")
        return_dt = data.get("return_datetime")

        # Validate required fields
        if not all([vehicle_id, pickup, return_dt]):
            return JsonResponse(
                {
                    "error": "vehicle_id, pickup_datetime and return_datetime are required"
                },
                status=400,
            )

        try:
            # Convert string dates to datetime objects
            pickup_dt = datetime.fromisoformat(pickup)
            return_dt_dt = datetime.fromisoformat(return_dt)

            # Validate date logic
            if pickup_dt >= return_dt_dt:
                return JsonResponse(
                    {"error": "Return datetime must be after pickup datetime"},
                    status=400,
                )

            vehicle = Vehicle.objects.get(id=vehicle_id)

            # Check for overlapping bookings
            overlapping = Order.objects.filter(
                vehicle=vehicle,
                pickup_datetime__lt=return_dt_dt,
                return_datetime__gt=pickup_dt,
                order_status__in=["upcoming", "ongoing"],
            ).exists()

            return JsonResponse(
                {
                    "available": not overlapping,
                    "vehicle_id": str(vehicle.id),
                    "pickup_datetime": pickup,
                    "return_datetime": return_dt,
                    "message": (
                        "Available"
                        if not overlapping
                        else "Not available for selected dates"
                    ),
                },
                status=200,
            )

        except ValueError:
            return JsonResponse(
                {
                    "error": "Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
                },
                status=400,
            )
        except Vehicle.DoesNotExist:
            return JsonResponse({"error": "Vehicle not found"}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
@csrf_exempt
def availability_calendar(request):
    """Get availability calendar for a vehicle"""
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            vehicle_id = data.get("vehicle_id")
        else:  # GET
            vehicle_id = request.GET.get("vehicle_id")

        if not vehicle_id:
            return JsonResponse({"error": "vehicle_id is required"}, status=400)

        try:
            vehicle = Vehicle.objects.get(id=vehicle_id)

            # Optionally get date range from request
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=90)

            # If custom date range provided in request
            if (
                request.method == "POST"
                and data.get("start_date")
                and data.get("end_date")
            ):
                try:
                    start_date = datetime.fromisoformat(data["start_date"]).date()
                    end_date = datetime.fromisoformat(data["end_date"]).date()
                    if start_date >= end_date:
                        raise ValueError("End date must be after start date")
                except ValueError as e:
                    return JsonResponse(
                        {"error": f"Invalid date format or range: {str(e)}"}, status=400
                    )

            bookings = Order.objects.filter(
                vehicle=vehicle,
                return_datetime__gte=start_date,
                pickup_datetime__lte=end_date,
                order_status__in=["upcoming", "ongoing"],
            ).values("pickup_datetime", "return_datetime")

            calendar = []
            for booking in bookings:
                calendar.append(
                    {
                        "start": booking["pickup_datetime"].isoformat(),
                        "end": booking["return_datetime"].isoformat(),
                        "status": "booked",
                    }
                )

            # Add available slots (optional)
            # This would require more complex date gap analysis

            return JsonResponse(
                {
                    "vehicle_id": str(vehicle.id),
                    "calendar": calendar,
                    "time_range": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat(),
                    },
                    "message": "Calendar retrieved successfully",
                }
            )

        except Vehicle.DoesNotExist:
            return JsonResponse({"error": "Vehicle not found"}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_POST
def cancel_order(request):
    """Cancel an existing order"""
    try:
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload"}, status=400)

        auth_token = data.get("authToken")
        order_id = data.get("order_id")

        if not all([auth_token, order_id]):
            return JsonResponse(
                {"error": "Both authToken and order_id are required"}, status=400
            )

        try:
            client = Client.objects.get(authToken=auth_token)
            order = Order.objects.get(id=order_id, client=client)

            # Get current time in timezone-aware format
            now = timezone.now()

            if order.order_status == "cancelled":
                return JsonResponse({"error": "Order is already cancelled"}, status=400)

            if order.order_status == "completed":
                return JsonResponse(
                    {"error": "Completed orders cannot be cancelled"}, status=400
                )

            # Compare with timezone-aware datetime
            if order.pickup_datetime < now:
                return JsonResponse(
                    {"error": "Orders with past pickup time cannot be cancelled"},
                    status=400,
                )

            order.order_status = "cancelled"
            order.save()

            return JsonResponse(
                {
                    "success": True,
                    "order_id": str(order.id),
                    "status": "cancelled",
                    "message": "Order cancelled successfully",
                    "refund_eligible": order.pickup_datetime > now,
                }
            )

        except Client.DoesNotExist:
            return JsonResponse({"error": "Invalid authToken"}, status=401)
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
