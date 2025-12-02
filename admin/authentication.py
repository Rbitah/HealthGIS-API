from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    #Serializer for user information
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser']
        read_only_fields = ['id', 'is_staff', 'is_superuser']


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    
    #Admin login endpoint
    
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check if user is admin
    if not user.is_staff:
        return Response(
            {'error': 'Access denied. Admin privileges required.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Login successful',
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    
   # Logout endpoint - blacklist the refresh token
    
   
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    
    #Get current authenticated user info
    
    
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    
   # Refresh access token
    
    
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response(
            {'error': 'Refresh token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            'access': str(refresh.access_token)
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': 'Invalid or expired refresh token'},
            status=status.HTTP_401_UNAUTHORIZED
        )
