from user.models import User
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema
from rest_framework import status, generics, permissions
from . import serializers
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.response import Response
from django.core.mail import send_mail

@extend_schema(tags=["User"])
class LoginTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.LoginTokenSerializer

@extend_schema(tags=["User"])
class SignupApi(generics.CreateAPIView):
    serializer_class = serializers.SignupSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user_email = response.data.get('email')
        return Response({'detail': 'User created successfully', 'email':user_email}, status=status.HTTP_201_CREATED)

@extend_schema(tags=["User"])
class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get(self, request):
        user = request.user
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(tags=["User"])
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UserProfileSerializer

    def get(self, request, username):
        user = User.objects.get(username=username)
        serializer = serializers.UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@extend_schema(tags=["User"])
class UpdateProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UpdateProfileSerializer

    def patch(self, request, username):
        try:
            user = User.objects.get(username=username)
            if user.username == request.user.username:
                serializer = serializers.UpdateProfileSerializer(user, data=request.data, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error:", "You dont have permission to update this profile."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error:", str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["User"])
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = serializers.ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new-password1'])
            user.save()
            return Response({"success": "Password Updated."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["User"])   
class PasswordResetView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = serializers.PasswordResetSerializers(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.validated_data['email'])
            token = PasswordResetTokenGenerator().make_token(user)
            reset_url = request.build_absolute_url(reverse('auth:password-reset-confirm')) + f"?token={token}&email={user.email}"

            subject = "Password Reset Request"
            message = f"""
                        You requested to reset your password.
                        Click to reset your password: {reset_url}.
                    """
            sender = "davidduyile6@gmail.com"
            receipient = [user.email]
            send_mail(
                subject,
                message,
                sender,
                receipient,
                fail_silently=False,
            )
            return Response({"success": "Password has been reset successfully. Check your mail."}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["User"])
class PasswordResetConfirmView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = serializers.PasswordResetConfirmSerializers(data=request.data)
        if serializer.is_valid():
            account = User.objects.get(email=serializer.validated_data['email'])
            account.set_password(serializer.validated_data['new_password'])
            account.save()
            return Response({"success":"Password has been reset successfully"}, status=status.HTTP_200_OK)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["User"])
class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.FollowSerializer

    def post(self, request):
        username = request.data.get("username")
        request_user = request.user

        try:
            user = User.objects.get(username=username)
            logged_in = User.objects.get(pk=request_user)
        except User.DoesNotExist:
            return Response({"error:", "User not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        if logged_in == user:
            return Response({"data":"You can't follow yourself"}, status=status.HTTP_403_FORBIDDEN)
        else:
            if user in logged_in.following.all():
                logged_in.following.remove(user)
                user.follower.remove(logged_in)
                is_following = False
            else:
                logged_in.following.add(user)
                user.follower.add(logged_in)
                is_following = True

        return Response({'is_following': is_following, "success": "User added to your following."}, status=status.HTTP_201_CREATED)
        