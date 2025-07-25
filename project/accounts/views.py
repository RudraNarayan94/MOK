from rest_framework.response import Response
from rest_framework import status 
from rest_framework.views import APIView 
from .serializers import *
from .renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache


class CustomToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token['username'] = user.username  
        return token
    
def get_tokens_for_user(user):
  refresh = CustomToken.for_user(user)

  return {
    'refresh' : str(refresh),
    'access' : str(refresh.access_token),
  }

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)  
            access_token = str(refresh.access_token)  

            return Response({"access": access_token}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        # token['username'] = user.username
        return Response({'token': token, 'msg': 'Registration Successful'},
                        status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token = get_tokens_for_user(user)

        return Response({'token': token, 'msg': 'Login Successful'}, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user_id = request.user.id
        cache_key = f"user_profile:{user_id}"
        data = cache.get(cache_key)

        if not data:
            serializer = UserProfileSerializer(request.user)
            data = serializer.data
            cache.set(cache_key, data, timeout=60 * 5)  # Cache for 5 minutes

        return Response(data, status=status.HTTP_200_OK)
    

class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
      serializer = UserChangePasswordSerializer(data = request.data, context={'user' : request.user})

      serializer.is_valid(raise_exception=True)
      return Response({'msg': 'Password Changed Successfully'},
                                  status=status.HTTP_200_OK)
      
  


class SendPasswordResetEmailView(APIView):
   renderer_classes = [UserRenderer]

   def post(self, request, format=None):
      serializer = SendPasswordResetEmailSerializer(data = request.data)

      serializer.is_valid(raise_exception = True)
      return Response({'msg': 'Password Reset link send. Please check your Email'},
                                status=status.HTTP_200_OK)
    
         
      
class UserPasswordResetView(APIView): 
   renderer_classes = [UserRenderer]

   def post(self, request, uid, token, format=None):
      serializer = UserPasswordResetSerializer(data = request.data, 
                                               context = {'uid':uid, 'token': token})

      serializer.is_valid(raise_exception = True)
      return Response({'msg': 'Password Reset Successfully'},
                                status=status.HTTP_200_OK)
        

