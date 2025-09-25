from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.accounts.models import *
from rest_framework_simplejwt.tokens import RefreshToken


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = [
            "id", "name", "address", "geo_lat", "geo_lng", "phone", "email", "description"
        ]



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'phone', 'is_active', 'last_login', 'role', 'office', 'account_type', 'date_joined'
        ]




class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'full_name', 'email', 'phone', 'is_active', 'last_login', 'role', 'office', 'account_type'
        ]



class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        extra_kwargs = { 'password' : { 'write_only': True }}
        fields = [
            'full_name', 'email', 'phone', 'password', 'role'
        ]


    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        return user



class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(help_text="Email or Phone")
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    # User info fields
    full_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    phone = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    account_type = serializers.CharField(read_only=True)
    office = serializers.CharField(read_only=True, source='office.name', default=None)

    def validate(self, attrs):
        identifier = attrs.get("identifier", "").strip()
        password = attrs.get("password")


        print("Identifier:", identifier)
        print("Password:", password)

        try:
            user = User.objects.get(models.Q(email__iexact=identifier) | models.Q(phone__iexact=identifier))
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email/phone or password")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email/phone or password.")

        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        
        # Partner verification check
        if user.role in ['partner_shop']:
            try:
                partner_profile = PartnerProfile.objects.get(user=user)
                if not partner_profile.is_verified:
                    raise serializers.ValidationError("Your account is under review. You will be notified upon verification.")
            except PartnerProfile.DoesNotExist:
                raise serializers.ValidationError("Your partner profile is incomplete or missing. Contact support.")
            
        
        refresh = RefreshToken.for_user(user)

        

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "account_type": user.account_type,
            "office": user.office.name if user.office else None,
        }
        




