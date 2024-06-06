from django.forms import ValidationError
from rest_framework import serializers

from django.utils import timezone

from django.utils.encoding import smart_str, DjangoUnicodeDecodeError, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .sheets import GoogleSheetProcessor
from .utils import UTIL

from .models import *
from core.settings import *

# Sheet Serializer
class SheetSerializer(serializers.Serializer):
    
    sheet_link = serializers.URLField(required=False)
    excel_file = serializers.FileField(required=False)
    
    project_link = serializers.URLField(required=True,error_messages={
                    'required': 'Project Link is required.',
                })
    
    class Meta:
        fields = ["sheet_url", "project_url", "excel_file"]
        
    def validate(self, attrs):
        user = self.context.get("user")
        project_link = attrs["project_link"]
        if bool("sheet_link" in attrs) == bool("excel_file" in attrs):
            raise ValidationError("Only One Sheet URL or Excel File is required. ")
        elif bool("sheet_link" in attrs):
            sheet_link = attrs["sheet_link"]
            
            pr = GoogleSheetProcessor(sheet=sheet_link, project_url=project_link, isFile=False)
            
            print(pr.__str__())
            # pr.get_episode()
            pr.save_full_episode_series_sequence(user)
            
        elif bool("excel_file" in attrs):
            excel_file = attrs["excel_file"]
            
            
            pr = GoogleSheetProcessor(sheet=excel_file, project_url=project_link, isFile=True)
            
            print(pr.__str__())
            # pr.get_episode()
            pr.save_full_episode_series_sequence(user)
        
        return super().validate(attrs)
        

# EPISDOE SERIALIZER

class EpisodeListSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    
    class Meta:
        model = EpisodeModel
        fields = ['id', 'title', 'content', 'start_time', 'end_time', 'sheet_link', 'project_link']
        
    def get_content(self, episode: EpisodeModel):
        return episode.content[:100] + "..."
        
        
class EpisodeDetailSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    title = serializers.CharField(required=True, max_length = 255, error_messages={
                    'required': 'Title is required.',
                    'max_length': 'Title must be less than 255 characters in length.',
                })
    content = serializers.CharField(required=True, error_messages={
                    'required': 'Content is required.',
                })
    start_time = serializers.CharField(required=True, error_messages={
                    'required': 'Start Time is required.',
                    'max_length': 'Start Time must be less than equal to 12 in length.',
                })
    end_time = serializers.CharField(required=True, error_messages={
                    'required': 'End Time is required.',
                    'max_length': 'End Time must be less than equal to 12 in length.',
                })
    sheet_link = serializers.URLField(required=True,error_messages={
                    'required': 'Sheet Link is required.',
                })
    project_link = serializers.URLField(required=True,error_messages={
                    'required': 'Project Link is required.',
                })
    
    class Meta:
        model = EpisodeModel
        fields = ['id', 'title', 'content', 'start_time', 'end_time', 'sheet_link', 'project_link']
        
# EPISODE SEQUENCES SERIALIZER

class SequenceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    words = serializers.CharField(required=True, max_length = 255, error_messages={
                    'required': 'Words is required.',
                    'max_length': 'Words must be less than 255 characters in length.',
                })
    sequence_number = serializers.IntegerField(required=True, error_messages={
                    'required': 'Sequence Number is required.',
                })
    
    start_time = serializers.CharField(required=True, error_messages={
                    'required': 'Start Time is required.',
                    'max_length': 'Start Time must be less than equal to 12 in length.',
                })
    end_time = serializers.CharField(required=True, error_messages={
                    'required': 'End Time is required.',
                    'max_length': 'End Time must be less than equal to 12 in length.',
                })
    
    class Meta:
        model = SequenceModel
        fields = ['id', 'words', 'sequence_number', 'start_time', 'end_time']

# CHAPTER SERIALIZERS

class ChapterListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ChapterModel
        fields = ['id', 'episode_id', 'title', 'content', 'start_time', 'end_time', "chapter_number"]
    
        
class ChapterDetailSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, max_length = 255, error_messages={
                    'required': 'Title is required.',
                    'max_length': 'Title must be less than 255 characters in length.',
                })
    content = serializers.CharField(required=True, error_messages={
                    'required': 'Content is required.',
                })
    start_time = serializers.CharField(required=True, error_messages={
                    'required': 'Start Time is required.',
                    'max_length': 'Start Time must be less than equal to 12 in length.',
                })
    end_time = serializers.CharField(required=True, error_messages={
                    'required': 'End Time is required.',
                    'max_length': 'End Time must be less than equal to 12 in length.',
                })
    
    chapter_number = serializers.IntegerField(required=True, error_messages={
                    'required': 'Chapter Number is required.',
                })
    # start_sequence_number = serializers.IntegerField(required=True, error_messages={
    #                 'required': 'Start Sequence Number is required.',
    #             })
    # end_sequence_number = serializers.IntegerField(required=True, error_messages={
    #                 'required': 'End Sequence Number is required.',
    #             })
    
    
    id = serializers.UUIDField(read_only=True)
    sequences = SequenceSerializer(many=True, read_only=True)
    episode_id = serializers.PrimaryKeyRelatedField(queryset=EpisodeModel.objects.all())
    
    class Meta:
        model = ChapterModel
        # fields = ['id', 'episode_id', 'title', 'content', 'start_time', 'end_time', 'start_sequence_number', "end_sequence_number", "chapter_number"]
        
        fields = ['id', 'episode_id', 'title', 'content', 'start_time', 'end_time', "sequences", "chapter_number"]
        

class ReelSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    sequences = SequenceSerializer(many=True, read_only=True)
    episode_id = serializers.PrimaryKeyRelatedField(queryset=EpisodeModel.objects.all())
    chapter_id = serializers.PrimaryKeyRelatedField(queryset=ChapterModel.objects.all())

    title = serializers.CharField(required=True, max_length = 255, error_messages={
                    'required': 'Title is required.',
                    'max_length': 'Title must be less than 255 characters in length.',
                })
    content = serializers.CharField(required=True, error_messages={
                    'required': 'Content is required.',
                })
    start_time = serializers.CharField(required=True, error_messages={
                    'required': 'Start Time is required.',
                    'max_length': 'Start Time must be less than equal to 12 in length.',
                })
    end_time = serializers.CharField(required=True, error_messages={
                    'required': 'End Time is required.',
                    'max_length': 'End Time must be less than equal to 12 in length.',
                })
    
    reel_number = serializers.IntegerField(required=True, error_messages={
                    'required': 'Reel Number is required.',
                })
    class Meta:
        model = ReelModel
        fields = ['id', 'episode_id', 'chapter_id', 'title', 'reel_number', 'sequences', 'content', 'start_time', 'end_time']



# AUTH SERIALIZERS
class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True, error_messages = {
                    'required': 'Password is required.',
                    'min_length': 'Password must be greater than 8 in length.'
                })
    password2 = serializers.CharField(write_only=True, min_length=8, required=True, error_messages = {
                    'required': 'Confirm password is required.'
                })
    
    class Meta:
        model = UserModel
        fields = ['password', 'password2']
    
    def validate(self, data):
        try:
            uid = self.context.get("uid")
            token = self.context.get("token")
            
            if data['password'] != data['password2']:
                raise serializers.ValidationError("Passwords do not match.")
            
            
            user_id = smart_str(urlsafe_base64_decode(uid))
            user = UserModel.objects.get(id = user_id)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Invalid or Outdated Password Reset Link.")
            
            user.set_password(data['password'])
            user.save()
        except DjangoUnicodeDecodeError as ex:
            
            raise serializers.ValidationError("Invalid or Outdated Password Reset Link.")
        return data

class UserPasswordForgotSerializer(serializers.Serializer):
    
    email = serializers.EmailField(required=True, error_messages={
                    'required': 'Email is required.',
                    'invalid': 'Enter a valid email address.'
                })
    
    class Meta:
        model = UserModel
        fields = ['email']
    
    def validate(self, data):
        email = data.get("email")
        user = UserModel.objects.filter(email=email)
        if user.exists():
            if user.filter(is_third_party = False).exists():
                fetched = user.first()
                print(email)
                uid = urlsafe_base64_encode(force_bytes(fetched.id))
                print("Encoded UID: ", uid)
                token = PasswordResetTokenGenerator().make_token(fetched)
                print("Token Generated: ", token)
                link = f'{FRONTEND_SERVER_URL}/api/auth/reset/{uid}/{token}'
                print("Password Reset Link: ", link)
                
                email_data = {
                    "subject": "Podcast: Reset Your Password",
                    "body": f"One Time password reset link. Valid for 15 minutes.\nClick on this link below to reset your password.\n{link}",
                    "to_email": fetched.email
                }
                UTIL.send_email(email_data)
            else:
                raise serializers.ValidationError("Social Account cannot forgot the password.")
        else:
            raise serializers.ValidationError("Account associated with this email does not exists.")
            
        # user.set_password(data['password'])
        # user.save()
        return data


class UserChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True, error_messages = {
                    'required': 'Password is required.',
                    'min_length': 'Password must be greater than 8 in length.'
                })
    password2 = serializers.CharField(write_only=True, min_length=8, required=True, error_messages = {
                    'required': 'Confirm password is required.'
                })
    
    class Meta:
        model = UserModel
        fields = ['password', 'password2']
    
    def validate(self, data):
        # user = self.context.get("user")
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        # user.set_password(data['password'])
        # user.save()
        return data

    
    def update(self, instance, validated_data):
        validated_data.pop('password2')
        return super().update(instance, validated_data)
    
    # def create(self, validated_data):
    #     validated_data.pop('password2')
    #     user = UserModel.objects.create_user(**validated_data)
    #     return user

class UserProfileSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(read_only=True, error_messages={
                    'required': 'Email is required.',
                    'invalid': 'Enter a valid email address.'
                })
    profile_image = serializers.ImageField(required=False)
    full_name = serializers.CharField(max_length=255, required=True, error_messages={
                    'required': 'Full name is required.',
                    'max_length': 'Full name cannot be longer than 255 characters.'
                })
    
    class Meta:
        model = UserModel
        fields = ['email', 'full_name', 'profile_image']
        read_only_fields = ['email']
        
    
    def validate_profile_image(self, image):
        # image = self.cleaned_data.get('profile_image', False)
        print(image.__dict__)
        if hasattr(image, "_file"):
            return image
        if image:
            # print(image)
            if image.size > 1*1024*1024:
                raise ValidationError("Image file too large ( > 1mb )")
            # setting unique image name
            id = str(uuid.uuid4())
            extension = image._name.split(".")[len(image._name.split("."))-1]
            image._name = id+"."+extension
            image.field_name = id
            # print(image.__dict__)
            
        return image
        

class UserLoginSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(required=True, error_messages={
                    'required': 'Email is required.',
                    'unique': 'An account with this email already exists.',
                    'invalid': 'Enter a valid email address.'
                })
    password = serializers.CharField(write_only=True, min_length=8, required=True, error_messages = {
                    'required': 'Password is required.',
                    'min_length': 'Password must be greater than 8 in length.'
                })
    
    class Meta:
        model = UserModel
        fields = ['email', 'password',]


class UserDetailSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(required=True, error_messages={
                    'required': 'Email is required.',
                    'unique': 'An account with this email already exists.',
                    'invalid': 'Enter a valid email address.'
                })
    full_name = serializers.CharField(max_length=255, error_messages={
                    'required': 'Full name is required.',
                    'max_length': 'Full name cannot be longer than 255 characters.'
                })
    password = serializers.CharField(write_only=True, min_length=8, required=True, error_messages = {
                    'required': 'Password is required.',
                    'min_length': 'Password must be greater than 8 in length.'
                })
    password2 = serializers.CharField(write_only=True, min_length=8, required=True, error_messages = {
                    'required': 'Confirm password is required.'
                })
    
    class Meta:
        model = UserModel
        fields = ['email', 'full_name', 'password', 'password2', 'profile_image', 'is_third_party']
        
    
    
    def validate_email(self, email):
        if UserModel.objects.filter(email=email).exists():
            raise ValidationError([
                'An account with this email already exists.'
            ])
        return email
        
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def update(self, instance, validated_data):
        validated_data.pop('password2')
        return super().update(instance, validated_data)
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = UserModel.objects.create_user(**validated_data)
        return user
    
    # def validate(self, 