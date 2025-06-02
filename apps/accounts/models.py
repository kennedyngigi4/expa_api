import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, fullname, phone, role, password=None):
        if not email:
            raise ValueError("Email is required")
        
        user = self.model(
            fullname=fullname,
            email=self.normalize_email(email).lower(),
            role=role,
            phone=phone,
        )
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user
    

    def create_superuser(self, email, fullname, phone, role, password=None):
        if not email:
            raise ValueError("Email is required")
        
        user = self.create_user(
            fullname=fullname,
            email=self.normalize_email(email).lower(),
            role=role,
            phone=phone,
            password=password,
        )
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def imagePath(instance, filename):
    return f"users/{instance.uid}/{filename}"

class User(AbstractBaseUser, PermissionsMixin):

    roles = [
        ( "Client", "Client", ),
        ( "Admin", "Admin", ),
        ( "Agent", "Agent", ),
        ( "Driver", "Driver", ),
    ]

    uid = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    gender = models.CharField(max_length=8, null=True, blank=True)
    profile_image = models.ImageField(upload_to=imagePath, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=60, default=roles[0][0], choices=roles, null=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    last_login = models.DateTimeField(auto_now=True, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)


    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "fullname", "phone", "role",
    ]

    def __str__(self):
        return str(self.email)



class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profiles", on_delete=models.CASCADE, null=True)
    account_type = models.CharField(max_length=50, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    warehouse = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.fullname
    

class DriverLocation(models.Model):
    driver = models.OneToOneField(User, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    vehicle_type = models.CharField(max_length=50, null=True, blank=True)
    vehicle_registration = models.CharField(max_length=20, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.driver.fullname} Location"



