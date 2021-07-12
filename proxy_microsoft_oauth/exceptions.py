class DNUAuthHookException(Exception):
    def __init__(self, *args, **kwargs):
        self.user__ = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
