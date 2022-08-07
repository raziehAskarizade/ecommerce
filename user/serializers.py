from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Profile, Address, UserPicture
from django.contrib.auth import get_user_model
from order.serializers import OrderSerializer

User = get_user_model()


class AddressSerializer(serializers.Serializer):
    class Meta:
        model = Address
        fields = '__all__'


class ImageSerializer(serializers.Serializer):
    user_profile = serializers.ImageField(required=False, use_url=True)
    user_signature = serializers.ImageField(required=False, use_url=True)

    class Meta:
        model = UserPicture
        fields = ('user_profile', 'user_signature')

    def create(self, validated_data):
        user = UserPicture.objects.create(**validated_data)
        return user

    def update(self, instance, validated_data):
        instance.user_profile = validated_data.get('user_profile', instance.user_profile)
        instance.user_signature = validated_data.get('user_signature', instance.user_signature)
        instance.save()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    # address = AddressSerializer(required=True)
    # order = OrderSerializer(required=False)

    class Meta:
        model = Profile
        fields = (
            'national_code', 'pictures', 'first_name', 'last_name', 'phone', 'address', 'order',
            'address',)


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone', 'password',)
        extra_kwargs = {'password': {'write_only': True}, }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone',)


class LoginUserSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        if phone and password:
            if User.objects.filter(phone=phone).exists():
                user = authenticate(request=self.context.get('request'),
                                    phone=phone, password=password)

            else:
                msg = {'detail': 'Phone number is not registered.',
                       'register': False}
                raise serializers.ValidationError(msg)

            if not user:
                # phone and password not matched
                msg = {
                    'detail': 'Unable to log in with provided credentials.', 'register': True}
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Used for both password change (Login required) and
    password reset(No login required but otp required)

    not using modelserializer as this serializer will be used for for two apis
    """

    password_1 = serializers.CharField(required=True)
    # password_1 can be old password or new password
    password_2 = serializers.CharField(required=True)
    # password_2 can be new password or confirm password according to apiview


class ForgetPasswordSerializer(serializers.Serializer):
    """
    Used for resetting password who forget their password via otp varification
    """
    phone = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
