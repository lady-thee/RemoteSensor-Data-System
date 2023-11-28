
from rest_framework import generics, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from api.models import User, Sensor, SensorData
from api.serializers import UserSerializer, SensorRegistrationSerializer
from api.signals import user_create_signal

""" Class Views APIs """

class ListAllUsersAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]

class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
        
        user_create_signal.send(sender=user.__class__, instance=user)
        return Response(
            {
                'message': 'User successfully created!'
            },
            status.HTTP_201_CREATED
        )        
        

class SensorRegistrationAPIView(generics.CreateAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorRegistrationSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]