import json
import uuid

from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework.decorators import api_view
from rest_framework.views import status

from .models import  Client, ClientDetails
from backend.settings import GOOGLE_CLIENT_ID


def create_client(username, email, password):
    try:
        if Client.objects.filter(email=email).exists():
            client = Client.objects.get(email=email)
            return str(client.authToken)
        client = Client(username=username, email=email, password=password)
        client.save()
        return str(client.authToken)
    except IntegrityError:
        return JsonResponse({"error": "Username already exists"}, status=409)


@csrf_exempt
@api_view(["POST"])
def register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")
            
            if not all([username, email, password]):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            auth_token = create_client(username, email, password)
            return JsonResponse(
                {
                    "token": auth_token,
                    "user_type": "Client",
                    "message": "Registration successful",
                },
                status=201,
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
@api_view(["POST"])
def google_login(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        
        id_token_str = data.get("id_token")
        username = data.get("username")
        email = data.get("email")

        if not all([id_token_str, username, email]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Verify Google ID token
        client_id = (
            GOOGLE_CLIENT_ID
        )
        idinfo = id_token.verify_oauth2_token(
            id_token_str, google_requests.Request(), client_id
        )

        if idinfo["email"] != email:
            return JsonResponse({"error": "Email does not match ID token"}, status=400)

        # Create or update client
        try:
            client, created = Client.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "password": str(uuid.uuid4()),  # Google users don’t need passwords
                },
            )
            if not created:
                # Update existing client if needed
                client.username = username
                client.authToken = uuid.uuid4()
                client.save()
            else:
                # New client, ensure authToken is set
                client.authToken = uuid.uuid4()
                client.save()
        except IntegrityError as e:
            return JsonResponse(
                {"error": "Email or username already exists"}, status=409
            )

        message = (
            "Google registration successful" if created else "Google login successful"
        )
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        
        return JsonResponse(
            {
                "token": str(client.authToken),
                "user_type": "Client",
                "message": message,
            },
            status=status_code,
        )

    except json.JSONDecodeError as e:
        return JsonResponse(
            {"error": "Invalid JSON format", "detail": str(e)}, status=400
        )
    except ValueError as e:
        return JsonResponse({"error": "Invalid ID token", "detail": str(e)}, status=400)
    except Exception as e:
        return JsonResponse(
            {"error": "Internal server error", "detail": str(e)}, status=500
        )


@csrf_exempt
@api_view(["POST"])
def login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            identifier = data.get("email")
            password = data.get("password")

            if not identifier or not password:
                return JsonResponse(
                    {"error": "Both identifier and password are required"}, status=400
                )

            

            # Check if identifier is an email (contains @) for Client
            if "@" in identifier:
                # Try to authenticate as Client
                try:
                    client = Client.objects.filter(
                        email=identifier, password=password
                    ).first()
                    if client:
                        new_token = uuid.uuid4()
                        client.authToken = new_token
                        client.save()
                        response_data = {
                            "user_type": "Client",
                            "token": str(client.authToken),
                        }
                        return JsonResponse(response_data)
                    else:
                        return JsonResponse({"error": "Invalid password"}, status=401)
                except Exception:
                    return JsonResponse(
                        {"error": "No client found with this email"}, status=404
                    )
            

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST method is allowed"}, status=405)


@csrf_exempt
@api_view(["POST"])
def add_client_details(request):
    if request.method == "POST":
        try:
            # Parse request body
            data = json.loads(request.body.decode("utf-8"))

            # Get auth token from headers or body
            auth_token = data.get("authToken")
            if not auth_token:
                return JsonResponse(
                    {"error": "Authorization token is required"}, status=400
                )

            try:
                # Find client by auth token
                client = Client.objects.get(authToken=auth_token)
            except Exception as e:
                return JsonResponse(
                    {"error": f"Invalid authentication token provided: {str(e)}"},
                    status=400,
                )

            # Validate and create client details
            try:
                name = data["name"]
                phone = data["phone"]
                gender = data["gender"]

                if ClientDetails.objects.filter(client=client).exists():
                    try:
                        cd = ClientDetails.objects.get(client=client)

                        cd.name = name
                        cd.phone = phone
                        cd.gender = gender
                        cd.save()
                    except:
                        return JsonResponse(
                            {
                                "success": False,
                                "message": "This Phone Number Already Registered",
                            },
                            status=401,
                        )

                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Client details updated successfully",
                        },
                        status=200,
                    )

                else:
                    try:
                        # Create or update client details
                        client_details = ClientDetails(
                            client=client, name=name, phone=phone, gender=gender
                        )

                        client_details.save()
                    except:
                        return JsonResponse(
                            {
                                "success": False,
                                "message": "This Phone Number Already Registered",
                            },
                            status=401,
                        )

                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Client details added successfully",
                        },
                        status=200,
                    )

            except KeyError as e:
                return JsonResponse(
                    {"error": f"Missing required field: {str(e)}"}, status=400
                )
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
@api_view(["POST"])
def get_client_details(request):
    if request.method == "POST":
        try:
            # Parse request body
            data = json.loads(request.body.decode("utf-8"))

            # Get auth token from request
            auth_token = data.get("authToken")
            if not auth_token:
                return JsonResponse(
                    {"error": "Authorization token is required"}, status=400
                )

            try:
                # Find client by auth token
                client = Client.objects.get(authToken=auth_token)
            except Exception:
                return JsonResponse(
                    {"error": "Invalid authentication token"}, status=401
                )

            try:
                # Get client details
                client_details = ClientDetails.objects.get(client=client)

                # Prepare response data
                response_data = {
                    "client": {
                        "username": client.username,
                        "email": client.email,
                    },
                    "details": {
                        "name": client_details.name,
                        "phone": client_details.phone,
                        "gender": client_details.gender,
                    },
                }

                return JsonResponse(
                    {
                        "success": True,
                        "data": response_data,
                        "message": "Client details retrieved successfully",
                    },
                    status=200,
                )

            except Exception as e:
                return JsonResponse(
                    {
                        "success": True,
                        "data": {
                            "client": {
                                "username": client.username,
                                "email": client.email,
                                "createdAt": client.createdAt,
                                "updatedAt": client.updatedAt,
                            },
                            "details": None,
                        },
                        "message": "Client exists but no details added yet",
                    },
                    status=200,
                )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)
