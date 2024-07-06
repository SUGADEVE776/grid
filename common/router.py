from contextlib import suppress

from rest_framework.routers import SimpleRouter

from common.helpers import random_n_token


class AppRouter(SimpleRouter):
    def get_default_basename(self, viewset):
        with suppress(AssertionError):
            return super().get_default_basename(viewset)

        return random_n_token()
