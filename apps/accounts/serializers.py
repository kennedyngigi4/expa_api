from rest_framework import serializers
from apps.accounts.models import User, Profile, DriverLocation
from apps.logistics.models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response

class ProfileSerializer(serializers.ModelSerializer):

    warehousename = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "account_type", "category", "warehouse", "warehousename"
        ]

    def get_warehousename(self, obj):
        try:
            warehouse = Warehouse.objects.using("logistics").get(wid=obj.warehouse)
            return warehouse.name
        except Warehouse.DoesNotExist:
            return None



class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    driverlocation = DriverLocationSerializer(required=False)
    profiles = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "uid","fullname", "email", "phone", "gender", "role", "date_joined", "is_active", "profiles", "driverlocation"
        ]


    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profiles", None)
        driver_data = validated_data.pop("driverlocation", None)


        # update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile data
        if profile_data:
            profile_instance = instance.profiles
            for attr, value in profile_data.items():
                setattr(profile_instance, attr, value)
            profile_instance.save()

        if driver_data:
            driver_instance = instance.driverlocation
            for attr, value in driver_data.items():
                setattr(driver_instance, attr, value)
            driver_instance.save()
            
        return instance



class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = { "write_only": { "password": True }}
        fields = [
            "fullname", "email", "phone", "role", "password", "created_by"
        ]

    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    
    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone already exists.")
        return value

    
    def create(self, validated_data):
        user = User.objects.create_user(
            fullname=validated_data['fullname'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            role=validated_data["role"],
            password=validated_data['password'],
        )

        return user
    


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        data.update({
            "id": str(self.user.uid),
            "name": self.user.fullname,
            "email": self.user.email,
            "phone": self.user.phone,
        })

        return data

