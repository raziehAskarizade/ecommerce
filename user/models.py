from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save
from django.contrib.auth.hashers import check_password

from testshoping import settings
from order.models import ListOrder


def only_digit(value):
    if value.isdigit() is False:
        raise TypeError('National code must be an integer!')


def upload_to_profile(instance, filename):
    return 'profile/{filename}'.format(filename=filename)


def upload_to_signature(instance, filename):
    return 'signature/{filename}'.format(filename=filename)


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, is_staff=False, is_active=True, is_admin=False):
        if not phone:
            raise ValueError('users must have a phone number')
        if not password:
            raise ValueError('user must have a password')

        user_obj = self.model(
            phone=phone
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, phone, password=None):
        user = self.create_user(
            phone,
            password=password,
            is_staff=True,

        )
        return user

    def create_superuser(self, phone, password=None):
        user = self.create_user(
            phone,
            password=password,
            is_staff=True,
            is_admin=True,

        )
        return user

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """


class User(AbstractBaseUser):
    id = models.BigAutoField(primary_key=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,14}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 13 digits "
                                         "allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=15, unique=True)
    name = models.CharField(max_length=20, blank=True, null=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    # cause we use username_field , phone is required and we don't need to add REQUIRED_FIELDS
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        permissions = (
            ("can_add_data", "can add a new data"),
        )

    def __str__(self):
        return self.phone

    def get_full_name(self):
        if self.name:
            return self.name
        return self.phone

    def get_short_name(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)


class Address(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.CharField(validators=[only_digit, MinLengthValidator(10)], max_length=10)
    country = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.id)


class UserPicture(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False)
    user_profile = models.ImageField(upload_to=upload_to_profile, null=True, blank=True)
    user_signature = models.ImageField(upload_to=upload_to_signature, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    national_code = models.CharField(validators=[only_digit, MinLengthValidator(10)], max_length=10)
    pictures = models.OneToOneField(UserPicture, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,14}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 13 digits "
                                         "allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=15, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(ListOrder, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.user)


class PhoneOTP(models.Model):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,14}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 14 digits "
                                         "allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    otp = models.CharField(max_length=9, blank=True, null=True)
    count = models.IntegerField(default=0, help_text='Number of otp sent')
    validated = models.BooleanField(default=False,
                                    help_text='If it is True, that means user have validate otp successfully in second '
                                              'API')

    def __str__(self):
        return str(self.phone) + ' is sent ' + str(self.otp)
