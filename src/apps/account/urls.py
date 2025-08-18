from django.urls import path

from .views import api_views, template_views

app_name = 'apps.account'


urlpatterns = [

    # api views
    path('api/token/refresh/', api_views.TokenRefresh.as_view(), name='api-token_refresh'),
    path('api/token/basic', api_views.LoginBasic.as_view(), name='api-token_obtain_pair_basic'),
    path('api/token/otp', api_views.LoginOTP.as_view(), name='api-token_obtain_pair_otp'),
    path('api/logout', api_views.Logout.as_view(), name='api-logout'),
    path('api/register', api_views.Register.as_view(), name='api-register'),
    path('api/reset-password', api_views.ResetPassword.as_view(), name='api-reset_password__send_code'),
    path('api/reset-password/check-code-and-set', api_views.ResetPasswordCheckAndSet.as_view(),
         name='api-reset_password__check_code_and_set'),
    path('api/user/send-otp-code', api_views.UserSendOTP.as_view(), name='api-user_send_otp_code'),
    path('api/user/profile/confirm-phone_number', api_views.ConfirmEmail.as_view(),
         name='api-user_profile_confirm_phone_number'),

    # templates views
    path('login/', template_views.LoginView.as_view(), name='login'),
    path('register/', template_views.RegisterView.as_view(), name='register'),
    path('logout/', template_views.logoutView.as_view(), name='logout'),
    path('password/reset/', template_views.GetPhoneNumberView.as_view(), name='get_phone_number'),
    path('password/reset/confirm/', template_views.ResetPassConfirmView.as_view(), name='reset_pass_confirm'),
    path('password/reset/complete/', template_views.ResetPassCompleteView.as_view(), name='reset_pass_complete'),
    path('register/send-code/', template_views.SendCodeView.as_view(), name='send_code'),
    path('register/verify/', template_views.VerifyEmailView.as_view(), name='verify_phone'),
    path('create-admin/', template_views.CreateAdminView.as_view(), name='create_admin'),
    path('profile/', template_views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', template_views.EditProfileView.as_view(), name='edit_profile'),
    path('users/', template_views.UserListView.as_view(), name='user_list'),
    path('blocklist/', template_views.UserBlockListView.as_view(), name='block_list'),
    path('users/<int:pk>/block/', template_views.BlockUserView.as_view(), name='block_user'),
    path('users/<int:pk>/unblock/', template_views.UnBlockUserView.as_view(), name='unblock_user'),
    path('users/<int:pk>/delete/', template_views.DeleteUserView.as_view(), name='delete_user'),
]
