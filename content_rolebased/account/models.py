import uuid

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
from django.core.exceptions import ValidationError
from .managers import CustomUserManager

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
   # These fields tie to the roles!
    ADMIN = 1
    MANAGER = 2
    CONTENT_MANAGER = 3

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (CONTENT_MANAGER, 'Content Writer')
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    # Roles created here
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    username = models.CharField(max_length=15, blank=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)
    created_by = models.EmailField(blank=True, null=True)
    modified_by = models.EmailField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.role in [self.ADMIN, self.MANAGER]

    @property
    def is_content_writer(self):
        return self.role == self.CONTENT_MANAGER


class Content(models.Model):
    DRAFT = 'DRAFT'
    ASSIGNED = 'ASSIGNED'
    PENDING_REVIEW = 'PENDING_REVIEW'
    APPROVED = 'APPROVED'

    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('ASSIGNED', 'Assigned'),
        ('PENDING_REVIEW', 'Pending Review'),
        ('APPROVED', 'Approved'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ASSIGNED')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_content',
        null = True,
        blank=True

    )
    last_modified_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='modified_content',
        null=True,
        blank=True

    )

    class Meta:
        db_table = 'content'


    def __str__(self):
        return self.title

    @property
    def is_editable(self):
        return self.status != self.APPROVED

    def can_edit(self, user):
        if self.status == self.APPROVED:
            return False
        if user.is_admin:
            return True
        return user.is_content_writer and hasattr(self, 'task') and self.task.assigned_to == user


class Task(models.Model):
    content = models.OneToOneField(Content, on_delete=models.CASCADE, related_name='task')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', null=True, blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', null=True, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.assigned_to and self.assigned_to.role != User.CONTENT_MANAGER:
            raise ValidationError("Tasks can only be assigned to content writers")
        if self.assigned_by and self.assigned_by.role not in [User.ADMIN, User.MANAGER]:
            raise ValidationError("Only managers and super admins can assign tasks")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'tasks'

class Feedback(models.Model):
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.user.role not in [User.ADMIN, User.MANAGER]:
            raise ValidationError("Only managers and super admins can provide feedback")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'feedback'