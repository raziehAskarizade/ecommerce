from datetime import timezone
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from django.contrib.auth import login
from knox.auth import TokenAuthentication
from knox.views import LoginView as KnoxLoginView
from .utils import otp_generator
from .serializers import (CreateUserSerializer, ChangePasswordSerializer,
                          UserSerializer, LoginUserSerializer, ForgetPasswordSerializer, ProfileSerializer,
                          ImageAddressSerializer)
from .models import User, PhoneOTP, Profile, UserPictureAddress
from django.shortcuts import get_object_or_404
from django.db.models import Q
import itertools
from rest_framework.views import APIView
from knox.models import AuthToken
from django.db.models.signals import pre_save


class LoginAPI(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        token_limit_per_user = self.get_token_limit_per_user()
        if token_limit_per_user is not None:
            now = timezone.now()
            token = request.user.auth_token_set.filter(expiry__gt=now)
            if token.count() >= token_limit_per_user:
                return Response(
                    {"error": "Maximum amount of tokens allowed per user exceeded."},
                    status=status.HTTP_403_FORBIDDEN
                )
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return super().post(request, format=None)

    def get_post_response_data(self, request, token, instance):
        data = {
            'expiry': self.format_expiry_datetime(instance.expiry),
            'token': token
        }
        return data


class UserAPI(generics.RetrieveAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordAPI(generics.UpdateAPIView):
    """
    Change password endpoint view
    """
    authentication_classes = (TokenAuthentication,)
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self, queryset=None):
        """
        Returns current logged in user instance
        """
        obj = self.request.user
        return obj

    # or update and change method put or patch
    # or post with method POST
    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get('password_1')):
                return Response({'detail': 'current_password Does not match with our data'},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get('password_2'))
            if serializer.data.get('password_1') == serializer.data.get('password_2'):
                return Response({'detail': 'old and new password are same'}, status=status.HTTP_400_BAD_REQUEST)
            self.object.password_changed = True
            self.object.save()
            return Response({'detail': 'Password has been successfully changed'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


######################################


def send_otp(phone):
    """
    This is an helper function to send otp to session stored phones or
    passed phone number as argument.
    """
    if phone:

        key = otp_generator()
        phone = str(phone)
        otp_key = str(key)
        # link = f'https://2factor.in/API/R1/?module=TRANS_SMS&apikey=fc9e5177-b3e7-11e8-a895-0200cd936042&to={phone}&from=wisfrg&templatename=wisfrags&var1={otp_key}'
        # result = requests.get(link, verify=False)
        return otp_key
    else:
        return False


def send_otp_forgot(phone):
    if phone:
        key = otp_generator()
        phone = str(phone)
        otp_key = str(key)
        user = get_object_or_404(User, phone__iexact=phone)
        if user.name:
            name = user.name
        else:
            name = phone
        # use all this in one line
        # link = f'https://2factor.in/API/R1/?module=TRANS_SMS&apikey=fc9e5177-b3e7-11e8-a895-0200cd936042&to={phone}&from=wisfgs&templatename=Wisfrags&var1={name}&var2={otp_key}'

        # result = requests.get(link, verify=False)
        # print(result)

        return otp_key
    else:
        return False


def phone_validate_in_classes(phone, otp):
    if otp:
        old = PhoneOTP.objects.filter(phone__iexact=phone)
        if old.exists():
            count = old.first().count
            old.update(count=count + 1)
            old.update(otp=otp)
            if count > 7:
                return Response({'detail': 'more than limited requested OTP!'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            count = 1
            PhoneOTP.objects.create(
                phone=phone,
                otp=otp,
                count=count)
    else:
        return Response({'detail': 'OTP send error!'}, status=status.HTTP_403_FORBIDDEN)
    return Response({'detail': 'otp sent!'}, status=status.HTTP_200_OK)


def class_user_object(user, data):
    serializer = ImageAddressSerializer
    serializer = serializer(data=dict(dict(list(data.data.items())[5:])))
    pic_add = 0
    if serializer.is_valid():
        data = serializer.save()

    # if user.pic_add is not None:
    #     pic_add = UserPictureAddress.objects.filter(id=int(str(user.pic_add))).update(
    #         user_signature=data.user_signature,
    #         user_profile=data.user_profile,
    #         address=data.address,
    #         city=data.city,
    #         postal_code=data.postal_code,
    #         country=data.country)
    # else:
    #     pic_add = UserPictureAddress.objects.create(user_signature=data.user_signature,
    #                                                 user_profile=data.user_profile, address=data.address,
    #                                                 city=data.city,
    #                                                 postal_code=data.postal_code, country=data.country)
    if pic_add == 0:
        return data
    return pic_add


def user_change_phone(sender, instance, *args, **kwargs):
    user = User.objects.filter(phone=instance.get('user'))
    if user.first() is not None and user.first() != instance.get('user'):
        raise Exception('same phone number')
    User.objects.filter(phone=instance.get('user')).update(phone=instance.get('phone'), name=instance.get('first_name'))


######################################


class EditProfile(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]
    serializer_class = ProfileSerializer
    serializer_im_add = ImageAddressSerializer

    def get_object(self, queryset=None):
        """
        Returns current logged in user instance
        """
        obj = self.request.user
        return obj

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile = Profile.objects.get(user=self.object)
        serialize = self.serializer_class(profile)
        pic_add = get_object_or_404(UserPictureAddress, id=int(str(profile.pic_add)))
        serializer_im_add = self.serializer_im_add(pic_add)
        finally_response = {**serialize.data, **serializer_im_add.data}
        return Response(finally_response)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.serializer_class(data=dict(itertools.islice(request.data.items(), 4)))
        if serializer.is_valid():
            profile = get_object_or_404(Profile, user=self.object)
            if profile is not None:
                profile = Profile.objects.filter(user=self.object)
                user_obj = class_user_object(profile.first(), request)
                try:
                    instance = {'user': self.object, 'phone': serializer.data.get('phone'),
                                'name': serializer.data.get('first_name')}
                    user_change_phone(sender=profile, instance=instance)
                except Exception:
                    return Response({'detail': 'this phone number is exist'}, status=status.HTTP_400_BAD_REQUEST)
                profile.update(
                    user=self.object,
                    first_name=serializer.data.get('first_name'),
                    last_name=serializer.data.get('last_name'),
                    national_code=serializer.data.get('national_code'),
                    pic_add=user_obj,
                    phone=serializer.data.get('phone'),
                )
                return Response({'detail': 'updated'}, status=status.HTTP_200_OK)
            return Response({'detail': 'user authentication with user profile doesnt match'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


pre_save.connect(receiver=user_change_phone, sender=EditProfile)


class ValidatePhoneSendOTP(APIView):
    '''
    # This class view takes phone number and if it doesn't exists already then it sends otp for first coming phone numbers
    '''

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                return Response({'detail': 'Phone Number already exists'}, status=status.HTTP_400_BAD_REQUEST)
            # logic to send the otp and store the phone number and that otp in table.
            else:
                otp = send_otp(phone)
                print(phone, otp)
                return phone_validate_in_classes(phone, otp)
        else:
            return Response({"detail": 'do it with post method!'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class ValidateOTP(APIView):
    '''
    If you have received otp, post a request with phone and that otp and you will be redirected to set the password
    '''

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp_sent = request.data.get('otp', False)

        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone__iexact=phone)
            if old.exists():
                otp = old.first().otp
                if str(otp) == str(otp_sent):
                    old.update(validated=True)
                    return Response({'detail': 'OPT matched'}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'OPT incorrect !'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'phone not recognized, try again!'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'phone or OTP were not received, try again!'},
                            status=status.HTTP_400_BAD_REQUEST)


class Register(generics.GenericAPIView):
    serializer_class = CreateUserSerializer
    '''Takes phone and a password and creates a new user only if otp was verified and phone is new'''

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        password = request.data.get('password', False)
        if phone and password:
            phone = str(phone)
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                return Response({'user is exist, try forgot password!'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                old = PhoneOTP.objects.filter(phone__iexact=phone)
                if old.exists():
                    if old.first().validated:
                        temp_data = {'phone': phone, 'password': password}
                        serializer = self.serializer_class(data=temp_data)
                        serializer.is_valid(raise_exception=True)
                        user = serializer.save()
                        user.save()
                        old.delete()
                        token = AuthToken.objects.create(user)
                        return Response({"token": token[1]})
                        # return Response({'token': f'{token}'}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'detail': 'your OPT not verified, try sent OTP first'},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'your phone number not recognized, try validate phone'},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'phone number or OPT nut received from POST method'},
                            status=status.HTTP_400_BAD_REQUEST)


class ValidatePhoneForgot(APIView):
    '''
    Validate if account is there for a given phone number and then send otp for forgot password reset'''

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                otp = send_otp_forgot(phone)
                print(phone, otp)
                return phone_validate_in_classes(phone, otp)
            else:
                return Response({'detail': 'Phone number not recognised'}, status=status.HTTP_400_BAD_REQUEST)


class ForgotValidateOTP(APIView):
    '''
    If you have received an otp, post a request with phone and that otp and you will be redirected to reset  the forgotten password'''

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp_sent = request.data.get('otp', False)

        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone__iexact=phone)
            if old.exists():
                otp = old.first().otp
                if str(otp) == str(otp_sent):
                    old.update(otp=otp_sent)
                    return Response({'detail': 'OTP matched,create new password'}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'OTP incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Phone not recognised'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'phone or otp was not received in Post request'},
                            status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordChange(APIView):
    '''
    if forgot_logged is valid and account exists then only pass otp, phone and password to reset the password. All there should match APIView'''

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp = request.data.get("otp", False)
        password = request.data.get('password', False)

        if phone and otp and password:
            old = PhoneOTP.objects.filter(Q(phone__iexact=phone) and Q(otp__iexact=otp))
            if old.exists():
                post_data = {
                    'phone': phone,
                    'password': password
                }
                user_obj = get_object_or_404(User, phone__iexact=phone)
                serializer = ForgetPasswordSerializer(data=post_data)
                serializer.is_valid(raise_exception=True)
                if user_obj:
                    user = User.objects.filter(phone__iexact=phone)
                    if user.first().check_password(serializer.data.get('password')):
                        return Response({'detail': 'old and new password are same!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                    user_obj.set_password(serializer.data.get('password'))
                    user_obj.active = True
                    user_obj.save()
                    old.delete()
                    return Response({'detail': 'Password changed,Login'}, status=status.HTTP_200_OK)

                else:
                    return Response({'detail': 'OTP Verification failed'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({'detail': 'Phone or otp are not matching'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'detail': 'try POST request'}, status=status.HTTP_400_BAD_REQUEST)
