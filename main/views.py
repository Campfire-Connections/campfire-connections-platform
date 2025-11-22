from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now


def healthcheck(request):
    payload = {
        "status": "ok",
        "timestamp": now().isoformat(),
    }
    try:
        connection.ensure_connection()
        payload["database"] = "ok"
    except DatabaseError:
        payload["database"] = "error"
        return JsonResponse(payload, status=503)
    return JsonResponse(payload)


def home(request):
    return render(request, "home.html")
