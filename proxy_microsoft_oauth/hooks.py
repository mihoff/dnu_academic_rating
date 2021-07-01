from proxy_microsoft_oauth.exceptions import DNUAuthHookException
from user_profile.models import Profile


def auth_hook(user, token):
    profile = Profile.objects.filter(user=user).first()
    if profile and profile.position is None:
        user.delete()
        raise DNUAuthHookException
