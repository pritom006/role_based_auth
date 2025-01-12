from .models import User, Content, Feedback, Task
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login

class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'username', 'role']

    def create(self, validated_data):
        role = validated_data.get('role', User.CONTENT_MANAGER)
        user = User(
            email = validated_data['email'],
            username = validated_data['username'],
            first_name=validated_data.get('first_name', ''),  # Add first_name
            last_name=validated_data.get('last_name', ''),
            role=validated_data['role']
        )
        
        user.set_password(validated_data['password'])
        if role == User.ADMIN:
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'role'
        )


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)



    def validate(self, data):
        email = data['email']
        password = data['password']
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid login credentials")

        try:
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)
            access_token = str(refresh.access_token)

            update_last_login(None, user)

            validation = {
                'access': access_token,
                'refresh': refresh_token,
                'email': user.email,
                'role': user.role,
            }

            return validation
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid login credentials")
        


# Content Serializer
class ContentSerializer(serializers.ModelSerializer):
    feedbacks = serializers.SerializerMethodField()

    class Meta:
        model = Content
        fields = ['id', 'title', 'content', 'status', 'created_at', 'updated_at',
                  'created_by', 'last_modified_by', 'feedbacks', 'is_editable']
        read_only_fields = ['created_by', 'last_modified_by', 'status', 'is_editable']

    def get_feedbacks(self, obj):
        return FeedbackSerializer(obj.feedbacks.all(), many=True).data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['last_modified_by'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['last_modified_by'] = self.context['request'].user
        return super().update(instance, validated_data)


# Feedback Serializer
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'content', 'user', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

# Task Serializer
class TaskSerializer(serializers.ModelSerializer):
    content = ContentSerializer(read_only=True)
    content_id = serializers.PrimaryKeyRelatedField(
        queryset=Content.objects.all(),
        source='content',
        write_only=True
    )
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'content', 'content_id', 'assigned_to', 'assigned_to_name',
                  'assigned_by', 'assigned_by_name', 'assigned_at']
        read_only_fields = ['assigned_by', 'assigned_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['assigned_by'] = user if user.is_admin else None
        return super().create(validated_data)
