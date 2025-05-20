from django.http import JsonResponse
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
def get_all_vehicles(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id, name, brand, vehicle_type, location, 
                price_per_day, price_per_hour, image_1, 
                current_status, rating, seating_capacity 
            FROM business_vehicle
        """)
        columns = [col[0] for col in cursor.description]
        vehicles = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

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
            cursor.execute("""
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
            """, [vehicle_id])

            row = cursor.fetchone()
            if not row:
                return JsonResponse({"error": "Vehicle not found"}, status=404)

            columns = [col[0] for col in cursor.description]
            vehicle = dict(zip(columns, row))

            # Type conversions
            vehicle["id"] = str(vehicle["id"])
            vehicle["owner_id"] = str(vehicle["owner_id"]) if vehicle["owner_id"] else None
            vehicle["price_per_day"] = float(vehicle["price_per_day"])
            vehicle["price_per_hour"] = float(vehicle["price_per_hour"])
            vehicle["security_deposit"] = float(vehicle["security_deposit"])
            vehicle["late_fee_per_hour"] = float(vehicle["late_fee_per_hour"])
            vehicle["rating"] = float(vehicle["rating"])
            vehicle["mileage"] = float(vehicle["mileage"])
            vehicle["current_odometer"] = float(vehicle["current_odometer"])
            vehicle["insurance_expiry_date"] = vehicle["insurance_expiry_date"].isoformat()

        return JsonResponse({"vehicle": vehicle})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)