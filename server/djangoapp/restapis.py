import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv("backend_url", default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    "sentiment_analyzer_url",
    default="http://localhost:5050/",
)


def get_request(endpoint, **kwargs):
    request_url = f"{backend_url.rstrip('/')}/{endpoint.lstrip('/')}"
    response = requests.get(request_url, params=kwargs or None, timeout=10)
    response.raise_for_status()
    return response.json()


def analyze_review_sentiments(text):
    encoded_text = quote(text, safe="")
    request_url = f"{sentiment_analyzer_url.rstrip('/')}/analyze/{encoded_text}"
    response = requests.get(request_url, timeout=10)
    response.raise_for_status()
    result = response.json()
    if not isinstance(result, dict):
        raise ValueError("Sentiment service returned an invalid response.")
    sentiment = result.get("sentiment")
    if sentiment not in {"positive", "neutral", "negative"}:
        raise ValueError("Sentiment service returned an invalid sentiment.")
    return sentiment


def post_review(data_dict):
    request_url = f"{backend_url.rstrip('/')}/insert_review"
    response = requests.post(request_url, json=data_dict, timeout=10)
    response.raise_for_status()
    return response.json()
