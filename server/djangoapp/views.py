import json
import requests
from pathlib import Path

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .restapis import analyze_review_sentiments, get_request, post_review


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


@require_GET
def get_dealerships(request, state="All"):
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    try:
        dealerships = get_request(endpoint)
    except (requests.RequestException, ValueError):
        return JsonResponse(
            {"status": 502, "message": "Unable to fetch dealerships."},
            status=502,
        )

    return JsonResponse({"status": 200, "dealers": dealerships})


@require_GET
def get_dealer_details(request, dealer_id):
    try:
        dealer_details = get_request(f"/fetchDealer/{dealer_id}")
    except (requests.RequestException, ValueError):
        return JsonResponse(
            {"status": 502, "message": "Unable to fetch dealership details."},
            status=502,
        )

    return JsonResponse({"status": 200, "dealer": dealer_details})


@require_GET
def get_dealer_reviews(request, dealer_id):
    try:
        reviews = get_request(f"/fetchReviews/dealer/{dealer_id}")
        if not isinstance(reviews, list):
            raise ValueError("Review service returned an invalid response.")
        for review in reviews:
            if not isinstance(review, dict) or not isinstance(review.get("review"), str):
                raise ValueError("Review service returned an invalid review.")
            review["sentiment"] = analyze_review_sentiments(review["review"])
    except requests.RequestException:
        return JsonResponse(
            {"status": 502, "message": "Unable to fetch or analyze dealer reviews."},
            status=502,
        )
    except ValueError as error:
        return JsonResponse(
            {"status": 502, "message": str(error)},
            status=502,
        )

    return JsonResponse({"status": 200, "reviews": reviews})


@csrf_exempt
@require_POST
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": 403, "message": "Unauthorized"},
            status=403,
        )

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"status": 400, "message": "Request body must be valid JSON."},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {"status": 400, "message": "Request body must be a JSON object."},
            status=400,
        )

    try:
        review = post_review(data)
    except (requests.RequestException, ValueError):
        return JsonResponse(
            {"status": 502, "message": "Error in posting review"},
            status=502,
        )

    return JsonResponse(
        {
            "status": 200,
            "message": "Review posted successfully",
            "review": review,
        }
    )


@require_GET
def get_cars(request):
    inventory_path = Path(__file__).resolve().parent.parent / "database" / "data" / "car_records.json"
    try:
        with inventory_path.open(encoding="utf-8") as inventory_file:
            inventory = json.load(inventory_file)
    except (OSError, json.JSONDecodeError):
        return JsonResponse(
            {"status": 500, "message": "Unable to load car inventory."},
            status=500,
        )

    cars = inventory.get("cars")
    if not isinstance(cars, list):
        return JsonResponse(
            {"status": 500, "message": "Car inventory has an invalid format."},
            status=500,
        )

    car_models = sorted(
        {
            (car["make"], car["model"])
            for car in cars
            if isinstance(car, dict)
            and isinstance(car.get("make"), str)
            and isinstance(car.get("model"), str)
        }
    )
    return JsonResponse(
        {
            "status": 200,
            "CarModels": [
                {"CarMake": make, "CarModel": model}
                for make, model in car_models
            ],
        }
    )


@require_GET
def analyze_review(request, review_text):
    try:
        sentiment = analyze_review_sentiments(review_text)
    except requests.RequestException:
        return JsonResponse(
            {"error": "Unable to analyze review sentiment."},
            status=502,
        )
    except ValueError as error:
        return JsonResponse({"error": str(error)}, status=502)

    return JsonResponse({"sentiment": sentiment})
