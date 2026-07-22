from django.shortcuts import redirect
from django.urls import resolve

class MustChangePasswordMiddleware:
    """
    Middleware that forces users with must_change_password=True flag to change
    their password before accessing any other page on the site.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and getattr(request.user, "must_change_password", False):
            # Resolve current path to get view details
            try:
                resolver_match = resolve(request.path_info)
                view_name = (
                    f"{resolver_match.app_name}:{resolver_match.url_name}"
                    if resolver_match.app_name
                    else resolver_match.url_name
                )
            except Exception:
                view_name = ""

            # Bypass list: password change view, logout view, and basic assets
            bypass_views = [
                "accounts:change_password",
                "accounts:logout",
                "admin:logout",
            ]

            is_asset = (
                request.path.startswith("/static/")
                or request.path.startswith("/media/")
                or "/js/" in request.path
                or "/css/" in request.path
            )

            # Redirect if they are requesting any other resource
            if view_name not in bypass_views and not is_asset and not request.path.startswith("/admin/"):
                return redirect("accounts:change_password")

        return self.get_response(request)
