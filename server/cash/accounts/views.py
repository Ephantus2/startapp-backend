# accounts/views.py

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, ReferralSerializer, NotificationSerializer
from .models import User, ReferralReward, Wallet, Activate, Notifications
from rest_framework import generics



def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        print("CONTENT TYPE:", request.content_type)
        print("DATA:", request.data)
        print("METHOD:", request.method)

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
                Notifications.objects.create(
                    title="Referral Joined",
                    notif_types="referral",
                    description=f"""{user} joined. You'll earn KES 200 once they are activated""",
                    user=user.referred_by
                )  
            
            Notifications.objects.create(
                title="Welcome to EarnKE",
                notif_types="system",
                description="Activate account and Complete your first task to start earning today!",
                user=user
            )
            

            return Response(
                {
                    'message': 'Account created successfully, please login',
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
                    'referral_link': f"https://earn-share.pages.dev/register?ref={user.referral_code}",
                    'from_referrals': user.from_referrals,
                    'life_term_earning': user.life_time_earning,
                    'phone_number': user.phone_number
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
        if user.activated:
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'points': user.points,
                'referral_code': user.referral_code,
                'referral_link': f"http://localhost:8080/register?ref={user.referral_code}"
            })
        return Response("Activate account to continue")


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
        
from django.contrib.auth import update_session_auth_hash
class UpdateProfile(APIView):
    permission_classes=[IsAuthenticated]
    
    def put(self, request, pk):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        phone = request.data.get('phoneNumber')
        
        if username:
            user.username = username
            user.save()
            Notifications.objects.create(
                title="Profile Updated",
                notif_types="system",
                description=f"""Username updated to {username}""",
                user=user
            )           
        if password:
            user.set_password(password)
            user.save()
            Notifications.objects.create(
                title="Profile Updated",
                notif_types="system",
                description=f"""Password updated""",
                user=user
            )  
            update_session_auth_hash(request, user)
        if phone:
            user.phone_number = phone
            user.save()
            Notifications.objects.create(
                title="Profile Updated",
                notif_types="system",
                description=f"""Phone number updated to {phone}""",
                user=user
            )  
        if email:
            user.email = email
            user.save()
            Notifications.objects.create(
                title="Profile Updated",
                notif_types="system",
                description=f"""Email updated to {email}""",
                user=user
            )  
        return Response({'message': 'profile updated'}, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        try:
            print(request.user)
            user = User.objects.get(email=request.user.email)
        except User.DoesNotExist():
            return Response({'error': 'user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        user.delete()
        return Response({'message': 'user deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
class NotificationsView(APIView):
    def get(self, request):
        Notification = Notifications.objects.filter(user=request.user)
        serializers = NotificationSerializer(Notification, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        Notification =  Notifications.objects.filter(user=request.user)
        Notification.update(read=True)
        