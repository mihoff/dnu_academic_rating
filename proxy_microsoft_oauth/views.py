from django.shortcuts import redirect

from django.contrib.auth import logout


def logout_view(request):
    logout(request)
    return redirect(  # Also need to log out from the Microsoft Identity platform
        "https://login.microsoftonline.com/common/oauth2/v2.0/logout"
        "?post_logout_redirect_uri=http://localhost:8000")
