from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import AuthenticationFailed

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
        user = User.objects.create_user(**validated_data)

        # Sending Welcome Email
        data = {
            "subject": "Welcome to MOK – Ready to Type Like a Speed Demon?",
            "body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                    <h2 style="color: #007bff;">🚀 Welcome to MOK, {user.username}! </h2>
                    <p>You've officially entered the <strong>Typing Speed Arena</strong>. 🏁</p>
                    <p>Get ready to shatter records, leave typos in the dust, and make your keyboard beg for mercy!</p>
                    
                    <h3 style="color: #28a745;">🔥 Pro Tip:</h3>
                    <p><em>"The spacebar is not just for breathing—it’s for winning!"</em></p>

                    <p>Speed is great, but accuracy? That’s the real flex. 😉</p>

                    <p style="text-align: center;">
                        <a href="http://localhost:3000" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: white; background-color: #007bff; text-decoration: none; border-radius: 5px;">Start Typing Now</a>
                    </p>

                    <p>See you at the leaderboard,</p>
                    <p><strong>The MOK Team</strong> 💻🔥</p>
                </div>
            </body>
            </html>
            """,
            "to_email": user.email,
        }
        EmailServices.send_email(data)
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
        data = {
            'subject': 'Your Password Has Been Changed Successfully',
            'body': f"""
            <html>
                <body>
                    <h2 style="color: #333;">Password Changed Successfully</h2>
                    <p>Dear <strong>{user.username}</strong>,</p>
                    <p>Your password has been successfully updated. If you made this change, no further action is needed.</p>
                    <p>If you did <strong>not</strong> request this change, please reset your password immediately and contact our support team.</p>
                    <p>Stay secure,<br><strong>MOK Security Team</strong></p>
                </body>
            </html>
            """,
            'to_email': user.email,
        }

        EmailServices.send_email(data)
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

            data = {
                'subject': 'Reset Your Password',
                'body': f"""
                <html>
                    <body>
                        <h2 style="color: #333;">Password Reset Request</h2>
                        <p>Dear <strong>{user.username}</strong>,</p>
                        <p>You have requested to reset your password. Click the button below to proceed:</p>
                        <p>
                            <a href="{link}" 
                                style="display: inline-block; padding: 10px 20px; font-size: 16px; color: white; background-color: #007BFF; text-decoration: none; border-radius: 5px;">
                                Reset Password
                            </a>
                        </p>
                        <p>If you did not request this, please ignore this email.</p>
                        <p>Stay secure,<br><strong>MOK Security Team</strong></p>
                    </body>
                </html>
                """,
                'to_email': user.email,
            }

            EmailServices.send_email(data)
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


