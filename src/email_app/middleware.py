import os
from django.http import JsonResponse

max_emails = os.getenv('JWT_ACCESS_TOKEN')
class JWTVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.valid_jwt = max_emails

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"success": False, "message": "Authorization header missing or invalid"}, status=401)

        token = auth_header.split(" ")[1]
        if token != self.valid_jwt:
            return JsonResponse({"success": False, "message": "Invalid or unauthorized token"}, status=403)
        return self.get_response(request)
