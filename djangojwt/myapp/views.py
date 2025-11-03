from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from myapp.models import Article
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, ArticlesSerializer
from .permissions import HasRole

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_serializer.data
            })
        else:
            return Response({'detail': 'Invalid credentials'}, status=401)

class DashboardView(APIView):
    permission_classes = [IsAuthenticated,HasRole]
    required_role = 'student'

    def get(self, request):
        user = request.user
        user_serializer = UserSerializer(user)
        return Response({
            'message': 'Welcome to dashboad',
            'user': user_serializer.data
        }, 200)
    

class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()   
    serializer_class = ArticlesSerializer 
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()   
    serializer_class = ArticlesSerializer 
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)