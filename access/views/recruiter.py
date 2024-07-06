from access.models import User
from access.serializers import RecruiterUserCreateSerializer
from common.views import AppCreateAPIView


class RecruiterUserCreateAPIView(AppCreateAPIView):
    serializer_class = RecruiterUserCreateSerializer
    queryset = User.objects.all()
