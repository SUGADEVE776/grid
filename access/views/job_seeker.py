from access.models import User
from access.serializers import UserCreateModelSerializer, UserListModelSerializer
from common.views import AppAPIView, AppModelListAPIViewSet


class UserCreateAPIView(AppAPIView):
    serializer_class = UserCreateModelSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_valid_serializer()
        serializer.save()
        return self.send_response(data=serializer.data)


class UserListAPIViewSet(AppModelListAPIViewSet):
    queryset = User.objects.all()
    serializer_class = UserListModelSerializer
