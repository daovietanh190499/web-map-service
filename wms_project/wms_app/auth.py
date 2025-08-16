from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.decorators import authentication_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Vui lòng cung cấp username và password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return Response({
                    'message': 'Đăng nhập thành công',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Tài khoản đã bị vô hiệu hóa'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Thông tin đăng nhập không chính xác'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({
            'message': 'Đăng xuất thành công'
        }, status=status.HTTP_200_OK)


class UserInfoView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'is_staff': request.user.is_staff,
                    'is_superuser': request.user.is_superuser
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Người dùng chưa đăng nhập'
            }, status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication, BasicAuthentication]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        if not username or not password or not email:
            return Response({
                'error': 'Vui lòng cung cấp username, email và password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kiểm tra username đã tồn tại
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Username đã tồn tại'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kiểm tra email đã tồn tại
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Email đã tồn tại'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            return Response({
                'message': 'Đăng ký thành công',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Có lỗi xảy ra khi đăng ký: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Function-based views for compatibility
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Function-based login view for compatibility"""
    view = LoginView()
    return view.post(request)


@api_view(['POST'])
def logout_view(request):
    """Function-based logout view for compatibility"""
    view = LogoutView()
    return view.post(request)


@api_view(['GET'])
def user_info_view(request):
    """Function-based user info view for compatibility"""
    view = UserInfoView()
    return view.get(request)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """Function-based register view for compatibility"""
    view = RegisterView()
    return view.post(request)
