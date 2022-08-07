from django.urls import path
from knox import views as knox_views
from .views import (UserAPI, ChangePasswordAPI, LoginAPI)

from .views import (ValidatePhoneSendOTP, ForgetPasswordChange, ValidateOTP, Register, ValidatePhoneForgot,
                    ForgotValidateOTP, EditProfile)

app_name = 'accounts'

urlpatterns = [

    # for registering a new user

    path("validate_phone/", ValidatePhoneSendOTP.as_view()),
    path("validate_otp/", ValidateOTP.as_view()),
    path("register/", Register.as_view()),
    path("change_password/", ChangePasswordAPI.as_view()),
    path("update_profile/", EditProfile.as_view()),

    # for forgot password

    path("forgot_validate_phone/", ValidatePhoneForgot.as_view()),
    path("forgot_validate_otp/", ForgotValidateOTP.as_view()),
    path("forgot_password/", ForgetPasswordChange.as_view()),

    # for login and logout

    path("login/", LoginAPI.as_view()),
    path("logout/", knox_views.LogoutView.as_view()),
    path("logoutall/", knox_views.LogoutAllView.as_view()),

    path("user/", UserAPI.as_view()),

]
