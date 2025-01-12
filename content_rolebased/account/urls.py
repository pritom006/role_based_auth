from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from . import views
from .views import (
    AuthUserRegistrationView,
    AuthUserLoginView,
    AuthUserLogoutView,
    UserListView
)
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('register', AuthUserRegistrationView.as_view(), name='register'),
    path('login', AuthUserLoginView.as_view(), name='login'),
    path('logout', AuthUserLogoutView.as_view(), name='logout'),
    path('users', UserListView.as_view(), name='users'),

    # Content URLs
    path('content/', views.ContentViewSet.as_view({'get': 'list', 'post': 'create'}), name='content-list'),
    path('content/<int:pk>/', views.ContentViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='content-detail'),
    path('content/<int:pk>/state/', views.ContentViewSet.as_view({'patch': 'state'}), name='content-state'),
    path('content/<int:pk>/approve/', views.ContentViewSet.as_view({'patch': 'approve'}), name='content-approve'),

    # Feedback URLs
    path('content/<int:content_pk>/feedback/', views.FeedbackViewSet.as_view({'get': 'list', 'post': 'create'}), name='content-feedback'),

    # Task URLs
    path('tasks/', views.TaskViewSet.as_view({'get': 'list', 'post': 'create'}), name='task-list'),
    path('tasks/<int:pk>/', views.TaskViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='task-detail'),
]
