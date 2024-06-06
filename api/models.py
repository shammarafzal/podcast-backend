from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid
from django.contrib.auth import get_user_model
from core.settings import *


# class EpisodeModel(models.Model):
#     id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    
#     title = models.CharField(max_length=255)
    
#     content = models.TextField(blank=True, null=True)
    
#     start_time = models.CharField(max_length=12)
#     end_time = models.CharField(max_length=12)
    
#     sheet_link = models.URLField(null=False, blank=False)
#     project_link = models.URLField(null=False, blank=False)
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.title

# class SequenceModel(models.Model):
#     id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    
#     episode_id = models.ForeignKey(EpisodeModel,  related_name='episodes', on_delete=models.CASCADE)
    
#     words = models.CharField(max_length=255)
    
#     sequence_number = models.PositiveBigIntegerField(null=False, blank=False)
    
#     start_time = models.CharField(max_length=12)
#     end_time = models.CharField(max_length=12)
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.title


# class ChapterModel(models.Model):
#     id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    
#     episode_id = models.ForeignKey(EpisodeModel, related_name='chapters', on_delete=models.CASCADE)
    
#     title = models.CharField(max_length=255)
    
#     chapter_number = models.PositiveBigIntegerField(null=False, blank=False)  # To maintain the order of chapters
    
#     start_sequence_number = models.PositiveBigIntegerField(null=False, blank=False)
#     end_sequence_number = models.PositiveBigIntegerField(null=False, blank=False)
    
#     content = models.TextField(blank=True, null=True)
#     start_time = models.CharField(max_length=12)
#     end_time = models.CharField(max_length=12)
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ('episode_id', 'chapter_number')
#         ordering = ['chapter_number']  # Default ordering by sequence_number

#     def __str__(self):
#         return f"{self.title} (Chapter {self.chapter_number})"

# class ReelModel(models.Model):
#     id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    
#     episode_id = models.ForeignKey(EpisodeModel, related_name='chapters', on_delete=models.CASCADE)
#     chapter_id = models.ForeignKey(ChapterModel, related_name='reels', on_delete=models.CASCADE)
    
#     title = models.CharField(max_length=255)
    
#     reel_number = models.PositiveBigIntegerField(null=False, blank=False)
    
#     start_sequence_number = models.PositiveBigIntegerField(null=False, blank=False)
#     end_sequence_number = models.PositiveBigIntegerField(null=False, blank=False)
    
#     content = models.TextField(blank=True, null=True)
#     start_time = models.CharField(max_length=12)
#     end_time = models.CharField(max_length=12)
    

#     class Meta:
#         unique_together = ('chapter_id', 'reel_number')

#     def __str__(self):
#         return f"Reel {self.reel_number}: {self.content[:30]}..."  # Display the first 30 characters of the text







class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        # extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, password, **extra_fields)


class UserModel(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    profile_image = models.ImageField(upload_to="uploads", null=True, default=None)
    is_active = models.BooleanField(default=True)
    is_third_party = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email
    
    

    

class EpisodeModel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    
    start_time = models.CharField(max_length=12, null=True)
    end_time = models.CharField(max_length=12, null=True)
    
    sheet_link = models.URLField()
    project_link = models.URLField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class SequenceModel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(EpisodeModel, related_name='sequences', on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    
    words = models.CharField(max_length=255)
    
    sequence_number = models.PositiveBigIntegerField()
    start_time = models.CharField(max_length=12, null=False)
    end_time = models.CharField(max_length=12, null=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.words

class ChapterModel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(EpisodeModel, related_name='chapters', on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=255)
    chapter_number = models.PositiveBigIntegerField()  # To maintain the order of chapters
    
    sequences = models.ManyToManyField(SequenceModel, related_name='chapters')
    
    content = models.TextField(blank=True, null=True)
    start_time = models.CharField(max_length=12, null=True)
    end_time = models.CharField(max_length=12, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('episode', 'chapter_number')
        ordering = ['chapter_number']

    def __str__(self):
        return f"{self.title} (Chapter {self.chapter_number})"

class ReelModel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(EpisodeModel, related_name='reels', on_delete=models.CASCADE)
    chapter = models.ForeignKey(ChapterModel, related_name='reels', on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    
    title = models.CharField(max_length=255)
    reel_number = models.PositiveBigIntegerField()
    
    sequences = models.ManyToManyField(SequenceModel, related_name='reels')
    
    content = models.TextField(blank=True, null=True)
    
    start_time = models.CharField(max_length=12, null=True)
    end_time = models.CharField(max_length=12, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('chapter', 'reel_number')

    def __str__(self):
        return f"Reel {self.reel_number}: {self.content[:30]}..."
