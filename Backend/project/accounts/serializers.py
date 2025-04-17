from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import AuthenticationFailed

from email_validator import validate_email, EmailNotValidError

from .utils import EmailServices
from .models import User

from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator



class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_username(self, value):
        if " " in value:
            raise serializers.ValidationError("Username cannot contain spaces.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        # Basic Syntax and MX record lookup
        try:
            valid = validate_email(value, check_deliverability=True)
            # valid["email"] is normalized
            email = valid["email"]
        except EmailNotValidError as e:
            raise serializers.ValidationError(str(e))
        
        # Role-Based Email Filtering
        prohibited_prefixes = ['support', 'info', 'admin', 'contact']
        local_part = email.split('@')[0]
        if local_part.lower() in prohibited_prefixes:
            raise serializers.ValidationError("Registration using role-based email addresses is not allowed.")
        
        # Disposable/Temporary Email Detection
        disposable_domains = ['mailinator.com', 'tempmail.com', '10minutemail.com']
        domain = email.split('@')[1].lower()
        if domain in disposable_domains:
            raise serializers.ValidationError("Disposable email addresses are not allowed.")
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already registered.")
        
        return email
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        # Send Email
        EmailServices.send_welcome_email(user)
        return user
    
  
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(username=email, password=password)  
        if user is None:
            raise AuthenticationFailed('Invalid email or password')

        # Updating last login timestamp
        update_last_login(None, user)

        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["id", "email", "username"]

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style=
    {'input_type': 'password'}, write_only=True)

    password2 = serializers.CharField(max_length= 255, style=
    {'input_type':'password'}, write_only=True)

    class Meta:
        fields = ["password", "password2"]
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')

        if not user:
            raise serializers.ValidationError("User context is missing.")
        
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")
        user.set_password(password)
        user.save()
        #send Email
        EmailServices.send_password_changed_email(user)
        return attrs


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            # Password reset link (frontend URL)
            link = f'http://localhost:3000/v1/api/user/reset/{uid}/{token}/'
            print('Password reset link:', link)            

            EmailServices.send_password_reset_email(user, link)
            return attrs
        else:
            raise serializers.ValidationError('You are not a registered user.')
        

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={'input_type': 'password'}, write_only=True
    )

    class Meta:
        fields = ["password", "password2"]

    def validate(self, attrs):
        password = attrs.get('password').strip()
        password2 = attrs.get('password2').strip()
        uid = self.context.get('uid')
        token = self.context.get('token')

        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password do not match.")

        try:
            user_id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=user_id)
        except (User.DoesNotExist, DjangoUnicodeDecodeError):
            raise serializers.ValidationError("Invalid or expired reset token.")

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Token is not valid or expired.")

        user.set_password(password)
        user.save()

        return {"message": "Password reset successfully"}


