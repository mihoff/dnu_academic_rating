from django.contrib.auth import logout
from django.contrib.sites.models import Site
from django.shortcuts import redirect, render
from microsoft_auth.utils import get_scheme
from microsoft_auth.views import AuthenticateCallbackView

from proxy_microsoft_oauth.exceptions import DNUAuthHookException


def logout_view(request):
    domain = Site.objects.get_current(request).domain
    scheme = get_scheme(request)
    logout(request)
    return redirect(  # Also need to log out from the Microsoft Identity platform
        f"https://login.microsoftonline.com/common/oauth2/v2.0/logout"
        f"?post_logout_redirect_uri={scheme}://{domain}/")


class AuthenticateCallbackViewOverwrite(AuthenticateCallbackView):

    def post(self, request):
        try:
            return super().post(request)
        except DNUAuthHookException as e:
            return render(
                request,
                "proxy_microsoft_oauth/auth_hook_exception.html",
                context={"user__": e.user__}
            )
