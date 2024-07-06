from django.urls import path

from access.views import (
    RecruiterUserCreateAPIView,
    UserCreateAPIView,
    UserListAPIViewSet,
    home,
)
from common.router import AppRouter

router = AppRouter()

URL_PREFIX = "user"

router.register(f"{URL_PREFIX}/list", UserListAPIViewSet, basename="user-list")


urlpatterns = [
    path("home/", home),
    # user
    path("user/create/", UserCreateAPIView.as_view()),
    path("recruiter/create/", RecruiterUserCreateAPIView.as_view()),
] + router.urls
