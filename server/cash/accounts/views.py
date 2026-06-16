# accounts/views.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, ReferralSerializer
from .models import User, ReferralReward, Wallet



def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            # reward referrer
            if user.referred_by:
                user.referred_by.points += 100
                user.referred_by.user_wallet += 200
                user.referred_by.save()

                ReferralReward.objects.create(
                    referrer=user.referred_by,
                    new_user=user,
                    points=100
                )

            return Response(
                {
                    'message': 'user created successfully',
                    'referral_code': user.referral_code
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(
            username=username,
            password=password
        )

        if user is not None:
            token = get_token_for_user(user)

            response = Response(
                {
                    'message': 'logged in successfully',
                    'user_id': user.id,
                    'user_name': user.username,
                    'date_joined': user.date_joined,
                    'email': user.email,
                    'referral_code': user.referral_code,
                    'points': user.points,
                    'user_wallet': user.user_wallet,
                    'referral_link': f"http://127.0.0.1:8000/accounts/register/?ref={user.referral_code}",
                    'from_referrals': user.from_referrals,
                    'life_term_earning': user.life_term_earning
                }
            )

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

        return Response(
            {'error': 'Invalid Credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    def post(self, request):
        response = Response({'message': 'logged out'})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'points': user.points,
            'referral_code': user.referral_code,
            'referral_link': f"http://127.0.0.1:8000/accounts/register/?ref={user.referral_code}"
        })


class ReferralHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rewards = ReferralReward.objects.filter(
            referrer=request.user
        ).order_by('-created_at')

        data = []

        for item in rewards:
            data.append({
                'new_user': item.new_user.username,
                'points': item.points,
                'date': item.created_at
            })

        return Response(data)
    
class MyReferralsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        referrals = request.user.people_referred.all()
        print(referrals)

        serializer = ReferralSerializer(
            referrals,
            many=True
        ) 

        return Response({
            "total_referrals": referrals.count(),
            "total_points": request.user.points,
            "referrals": serializer.data
        })