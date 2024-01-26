import pdb
import requests
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import authenticate, login, logout
from django.http import Http404

from api.models import User, Sensor, SensorData
from api.serializers import (UserSerializer,
                             SensorRegistrationSerializer, 
                             LoginSerializer,
                             SensorDataSerializer,
                             SensorSettingsSerializer,
                             SensorDataDetailsSerializer,
                             PasswordResetSerializer,
                             ProfileSettingsSerializer
                             )
from api.signals import user_create_signal
from api.factory import UserFactory



""" Class Views APIs """

# For admin priviledges
class ListAllUsersAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    
    
class ListAllSensorsAPIView(generics.ListAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSettingsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    

# User APIs for User CRUD Operations
class UserRegistrationAPIView(generics.CreateAPIView):
    """
    API view class that handles user registration/creation
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    
    def create(self, request, *args, **kwargs):
        dummy_data = UserFactory() # Dummy data 
        if request.data:
            serializer = self.get_serializer(data=request.data)
        else:
            serializer = self.get_serializer(data=dummy_data.__dict__)
            
        serializer.is_valid(raise_exception=True)
        user = serializer.create(serializer.validated_data)
    
        user_create_signal.send(sender=user.__class__, instance=user)
        return Response(
            {
                'message': 'User successfully created!'
            },
            status.HTTP_201_CREATED
        )  

class ChangePasswordAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PasswordResetSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        # print(self.request.method)
        self.object = self.get_object()
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if hasattr(user, "auth_token"):
            user.auth_token.delete()
        Token.objects.get_or_create(user=user)
        return Response({"message": "Password Reset Successful!"}, status.HTTP_200_OK)


class UserLoginAPIView(APIView):
    """
    API view class that handles authentication and user login
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(request,
                            username=serializer.validated_data.get('email'),
                            password=serializer.validated_data.get('password')
                            )
        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {'message': 'Logged In Successfully!',
                 'token': str(token.key)
                },
                status.HTTP_200_OK
            )
        else:
            return Response(
                {'message': 'Email or password does not match any account!'},
                status.HTTP_400_BAD_REQUEST
            )
            

class LogoutAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        try:
            Token.objects.filter(user=request.user).delete()
            logout(request)
            return Response({"message": "Successfully logged out!"}, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status.HTTP_400_BAD_REQUEST)



class RetrieveUpdateDeleteUserAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSettingsSerializer
    # authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    
    def get_object(self):
        if not self.request.user.is_authenticated:
            return Response({'detail': 'You have to log in to view this page!'},
                            status.HTTP_401_UNAUTHORIZED)
        user_email = self.request.user.email 
        user_id = User.objects.filter(email=user_email).values_list('id', flat=True).get()
        obj = User.objects.get(id=user_id)
        
        return obj

    def get(self, request, *args, **kwargs):
        account = self.get_object()
        serializer = self.get_serializer(account)
        return Response(serializer.data, status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        account = self.get_object()
        serializer = self.get_serializer(account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Details Updated Successfully!", "detail": serializer.data},
            status.HTTP_200_OK
        )
    def delete(self, request, *args, **kwargs):
        account = self.get_object()
        account.delete()
        
        return Response(
            {'message': 'Account Deleted Successfully!'},
            status.HTTP_204_NO_CONTENT
        )


# Sensor API Classes For Handling Sensor Registration and Authentication

class SensorRegistrationAPIView(generics.CreateAPIView):
    """
    API view class that handles Sensor registration
    """
    queryset = Sensor.objects.all()
    serializer_class = SensorRegistrationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    

class SensorDataAPIView(generics.CreateAPIView):
    """
     API view class that handles saving data from a registered sensor
    """
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    
    

class SensorDataDetailAPIView(generics.ListAPIView):
    """
     API view class that handles retrieving data from a registered sensor
    """
    queryset = SensorData.objects.all()
    serializer_class = SensorDataDetailsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]


class RetrieveSensorAPIView(generics.RetrieveAPIView):
    serializer_class = SensorSettingsSerializer
    queryset = Sensor
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    
    
    def get_object(self):
        try:
            sensor_id = self.kwargs['pk']
            return Sensor.objects.get(id=sensor_id, operator=self.request.user)
        except Sensor.DoesNotExist:
            raise Http404



class RetrieveUpdateDeleteSensorAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSettingsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    
    # def get_object(self):
    #     """This method retrieves the authenticated user/operator and return the id of the request.user"""
        
    #     if not self.request.user.is_authenticated:
    #         return Response({'detail': 'You have to log in to view sensors!'},
    #                         status.HTTP_401_UNAUTHORIZED)
    #     user_email = self.request.user.email
    #     user_id = User.objects.filter(email=user_email).values_list("id", flat=True).get()
    #     obj = User.objects.get(id=user_id)
        
    #     return obj
        
    def get_queryset(self):
            """This method retrieves sensors associated with the authenticated user."""
            if not self.request.user.is_authenticated:
                return Sensor.objects.none()
            
            return Sensor.objects.filter(operator=self.request.user)
    
    def get(self, request, *args, **kwargs):
        """This method gets the sensors registered under the current user/operator."""
        sensors = self.get_queryset()
        serializer = self.get_serializer(sensors, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    
    
        # operator = self.get_object()
        # sensor = Sensor.objects.get(operator=operator)
        # serializer = self.get_serializer(sensor)
        # return Response(serializer.data, status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        """ This method updates the sensor registered under the current user/operator """
        
        sensor = self.get_object()
        serializer = self.get_serializer(sensor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Details Updated Successfully!", "detail": serializer.data},
            status.HTTP_200_OK
        )
    
    def delete(self, request, *args, **kwargs):
        """ This method deletes the sensor registered under the current user/operator """
        
        sensor = self.get_object()
        sensor.delete()
        
        return Response(
            {'message': 'Sensor Deleted Successfully!'},
            status.HTTP_204_NO_CONTENT
        )