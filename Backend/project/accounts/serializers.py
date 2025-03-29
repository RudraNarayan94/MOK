from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import AuthenticationFailed

from .utils import Util
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

    def validate_username(self, value): #Todo : Classic Username validation
        if " " in value:
            raise serializers.ValidationError("Username cannot contain spaces.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
  
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(username=email, password=password)  # `username` is required for `authenticate()`
        if user is None:
            raise AuthenticationFailed('Invalid email or password')

        # Update last login timestamp
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

        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match")
        user.set_password(password)
        user.save()
        #send Email
        # data= {
        #     'subject':'Your Password Has Been Changed Successfully ',
        #     'body':"",
        #     'to_email':user.email,
        # }
        # Util.send_email(data)
        return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email = email).exists():
            user = User.objects.get(email = email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            # Reminder : '{ClientURL}/v1/api/user/reset/'+uid+'/'+token+'/'
            link = 'http://localhost:3000/v1/api/user/reset/'+uid+'/'+token+'/'
            print('password reset link', link)
            #send Email
            data= {
                'subject':'Reset Your Password',
                'body':"",
                'to_email':user.email,
            }
            Util.send_email(data)
            return attrs

        else:
            raise serializers.ValidationError('You are not a Registered User')

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length= 255, style=
    {'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length= 255, style=
    {'input_type':'password'}, write_only=True)
    class Meta:
        fields = ["password", "password2"]
    
    def validate(self, attrs):
        try :
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')

            if password != password2:
                raise serializers.ValidationError("Password and Confirm Password doesn't match")
            
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id = id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is not valid or expired")
            
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("Token is not valid or expired")


