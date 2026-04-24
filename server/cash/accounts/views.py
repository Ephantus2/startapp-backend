from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request):
        serializedData = UserSerializer(data = request.data)
        if serializedData.is_valid():
            serializedData.save()
            return Response({'message': 'user created successfully, please login'}, status=status.HTTP_201_CREATED)
        return Response(serializedData.errors, status=status.HTTP_400_BAD_REQUEST)
    

def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return({
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    })
    
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user =  authenticate(username=username, password=password)
        
        if user is not None:
            token = get_token_for_user(user)
            response = Response({'message': 'logged in successfully', "user": user.id})
            response.set_cookie(
                key='access_token',
                value=token['access'],
                httponly=True,
                samesite='None',
                secure=True
            )
            response.set_cookie(
                key='refresh_token',
                value=token['refresh'],
                httponly=True,
                samesite='None',
                secure=True
            )
            return response
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        response.data = {'message': 'logged out'}
        return response