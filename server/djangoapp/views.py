import json

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST


@csrf_exempt
@require_POST
def login_user(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Request body must be valid JSON."}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({"error": "Request body must be a JSON object."}, status=400)

    username = data.get("userName")
    password = data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return JsonResponse(
            {"error": "Both userName and password are required."},
            status=400,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"userName": username, "status": "Authentication Failed"})

    login(request, user)
    return JsonResponse({"userName": username, "status": "Authenticated"})


@require_GET
def logout_user(request):
    logout(request)
    return JsonResponse({"userName": ""})


@csrf_exempt
@require_POST
def registration(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Request body must be valid JSON."}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({"error": "Request body must be a JSON object."}, status=400)

    fields = ("userName", "password", "firstName", "lastName", "email")
    if any(not isinstance(data.get(field), str) or not data[field].strip() for field in fields):
        return JsonResponse({"error": "All registration fields are required."}, status=400)

    username = data["userName"].strip()
    email = data["email"].strip()
    user_model = get_user_model()
    if user_model.objects.filter(username__iexact=username).exists():
        return JsonResponse({"userName": username, "error": "Already Registered"})
    if user_model.objects.filter(email__iexact=email).exists():
        return JsonResponse({"userName": username, "error": "Email already registered"})

    user = user_model.objects.create_user(
        username=username,
        password=data["password"],
        first_name=data["firstName"].strip(),
        last_name=data["lastName"].strip(),
        email=email,
    )
    login(request, user)
    return JsonResponse({"userName": username, "status": "Authenticated"})
