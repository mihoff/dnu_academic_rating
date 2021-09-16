import logging

from proxy_microsoft_oauth.exceptions import DNUAuthHookException
from user_profile.models import Profile

logger = logging.getLogger()


def auth_hook(user, token):
    profile = Profile.objects.filter(user=user).first()
    if profile and profile.position is None:
        logger.error(f"Office365 authentication failed :: {user} <{token}>")
        user.delete()
        raise DNUAuthHookException(user=user)
