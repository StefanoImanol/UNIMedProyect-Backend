from django.http import JsonResponse
import json

class JSONMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.content_type == "application/json" and request.body:
            try:
                request.json = json.loads(request.body)
            except ValueError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
        else:
            request.json = {}
        return self.get_response(request)
