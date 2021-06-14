from proxy_microsoft_oauth.exceptions import DNUAuthHookException
from proxy_microsoft_oauth.models import AllowedMicrosoftAccount


def auth_hook(user, token):
    for i in AllowedMicrosoftAccount.objects.all():
        if i.tail and not user.username.endswith(i.tail):
            raise DNUAuthHookException
