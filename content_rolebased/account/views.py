from django.shortcuts import render
from rest_framework import status, viewsets, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserListSerializer,
    ContentSerializer,
    FeedbackSerializer,
    TaskSerializer
)

from .models import User, Content, Task, Feedback


class AuthUserRegistrationView(APIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            serializer.save()
            status_code = status.HTTP_201_CREATED

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'User successfully registered!',
                'user': serializer.data
            }

            return Response(response, status=status_code)
        

class AuthUserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)

        if valid:
            status_code = status.HTTP_200_OK

            response = {
                'success': True,
                'statusCode': status_code,
                'message': 'User logged in successfully',
                'access': serializer.data['access'],
                'refresh': serializer.data['refresh'],
                'authenticatedUser': {
                    'email': serializer.data['email'],
                    'role': serializer.data['role']
                }
            }

            return Response(response, status=status_code)


class UserListView(APIView):
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        if user.role != 1:
            response = {
                'success': False,
                'status_code': status.HTTP_403_FORBIDDEN,
                'message': 'You are not authorized to perform this action'
            }
            return Response(response, status.HTTP_403_FORBIDDEN)
        else:
            users = User.objects.all()
            serializer = self.serializer_class(users, many=True)
            response = {
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Successfully fetched users',
                'users': serializer.data

            }
            return Response(response, status=status.HTTP_200_OK)


class AuthUserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"success": False, "message": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()  # This will blacklist the refresh token

            return Response(
                {"success": True, "message": "User logged out successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsContentWriter(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_content_writer
    
class IsAdminOrContentWriter(permissions.BasePermission):
    """
    Custom permission to only allow admins or content writers to create/edit content.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return False
            
        # Allow admin and content writer to create/edit
        return request.user.is_admin or request.user.is_content_writer

class IsContentOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a content or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Check if content is editable
        if not obj.is_editable:
            return False
            
        # Allow admin to edit any content
        if request.user.is_admin:
            return True
            
        # Check if content writer is assigned to this content
        return (request.user.is_content_writer and 
                hasattr(obj, 'task') and 
                obj.task.assigned_to == request.user)


class ContentViewSet(viewsets.ModelViewSet):
    serializer_class = ContentSerializer
    permission_classes = [IsAdminOrContentWriter, IsContentOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Content.objects.all()
        elif user.is_content_writer:
            return Content.objects.filter(task__assigned_to=user)
        return Content.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin or user.is_content_writer:
            serializer.save(created_by=user)
        else:
            raise PermissionDenied("You do not have permission to create content.")

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def state(self, request, pk=None):
        content = self.get_object()
        new_status = request.data.get('status')

        if new_status not in dict(Content.STATUS_CHOICES):
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        content.status = new_status
        content.last_modified_by = request.user
        content.save()
        return Response(self.get_serializer(content).data)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        content = self.get_object()
        content.status = 'APPROVED'
        content.last_modified_by = request.user
        content.save()
        return Response(self.get_serializer(content).data)

    @action(detail=False, methods=['get'], permission_classes=[IsContentWriter])
    def assigned(self, request):
        user = request.user
        queryset = Content.objects.filter(task__assigned_to=user)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def approved(self, request):
        queryset = Content.objects.filter(status='APPROVED')
        return Response(self.get_serializer(queryset, many=True).data)


class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        content_id = self.kwargs.get('content_pk')
        return Feedback.objects.filter(content_id=content_id)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_admin:
            serializer.save(user=user)
        else:
            raise PermissionDenied("Only admins can provide feedback.")


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()