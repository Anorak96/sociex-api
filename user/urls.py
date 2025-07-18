from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'user_api'
urlpatterns = [
    path('', views.UserView.as_view(), name='user'),
    path('<str:username>', views.UserProfileView.as_view(), name='profile'),
    path('<str:username>/update', views.UpdateProfileView.as_view(), name='update_profile'),

    path('follow/', views.FollowUserView.as_view(), name='follow_user'),
    
    path('auth/signup', views.SignupApi.as_view(), name='signup'),
    path('auth/login', views.LoginTokenObtainPairView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('auth/change-password', views.ChangePasswordView.as_view(), name='change-password'),
    path('auth/password-reset-request', views.PasswordResetView.as_view(), name='password-reset-request'),
    path('auth/password-reset-confirm', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]