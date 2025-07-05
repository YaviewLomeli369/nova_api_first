# core/middleware/auditoria.py

from accounts.signals import set_audit_user

class AuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            set_audit_user(request.user)
        response = self.get_response(request)
        return response