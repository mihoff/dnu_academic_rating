from microsoft_auth.backends import MicrosoftAuthenticationBackend


class ProxyMicrosoftAuthenticationBackend(MicrosoftAuthenticationBackend):

    def _get_user_from_microsoft(self, data):
        """
        Dirty hack to lowercase income email from Microsoft response,
        since microsoft_auth package does not provide hooks to customize decoded response before processing.
        """
        user = None
        microsoft_user = self._get_microsoft_user(data)

        if microsoft_user is not None:
            data["email"] = data["email"].lower()
            user = self._verify_microsoft_user(microsoft_user, data)

        return user
