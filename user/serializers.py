from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from user.models import User
from post.models import Post, Image
from post.serializers import PostSerializer, ImageSerializer

class LoginTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        return token

class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields don't match."})
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
        )
        user.set_password(validated_data['password1'])
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'bio', 'cover_pic', 'profile_pic')

class UserProfileSerializer(serializers.ModelSerializer):
    posts = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    follower = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    suggest_user = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    def get_posts(self, obj):
        request = self.context.get('request', None)
        posts = Post.objects.filter(user=obj)
        return PostSerializer(posts, many=True, context={'request': request}).data

    def get_following(self, obj):
        following = obj.get_following()
        return UserSerializer(following, many=True).data

    def get_follower(self, obj):
        follower = obj.get_follower()
        return UserSerializer(follower, many=True).data

    def get_photos(self, obj):
        images = Image.objects.filter(post__user=obj).order_by('post')
        if images:
            return ImageSerializer(images, many=True).data

    def get_suggest_user(self, obj):
        users = User.objects.all().exclude(pk=obj)
        my_user = User.objects.get(pk=obj)
        avail = [user for user in users if user not in my_user.get_following()]
        return UserSerializer(avail, many=True).data

    def get_is_following(self, obj):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            user = request.user
            my_profile = User.objects.get(username=user)
            other_profile = User.objects.get(username=obj.username)

            if my_profile == other_profile:
                return "This is your profile"

            if my_profile in other_profile.follower.all():
                return True
            else:
                return False

    class Meta:
        model = User
        fields = ('email', 'username', 'bio', 'cover_pic', 'profile_pic', 'posts', 'photos', 'following', 'follower', 'suggest_user', 'is_following')

class UpdateProfileSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(required=False)
    cover_pic = serializers.ImageField(required=False)
    bio = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ('email', 'profile_pic', 'cover_pic', 'bio')

    def validate(self, data):
        request = self.context.get('request')
        data["email_sent"] = "email" in request.data
        data["profile_pic_sent"] = "profile_pic" in request.data
        data["cover_pic_sent"] = "cover_pic" in request.data
        data["bio_sent"] = "bio" in request.data
        return data

    def update(self, instance, validated_data):
        email_sent = validated_data.pop("email_sent", False)
        profile_pic_sent = validated_data.pop("profile_pic_sent", False)
        bio_sent = validated_data.pop("bio_sent", False)
        cover_pic_sent = validated_data.pop("cover_pic_sent", False)

        if email_sent:
            new_email = validated_data.get('email')
            if new_email and new_email != instance.email:
                instance.email = new_email
        
        if bio_sent:
            new_bio = validated_data.get('bio')
            if new_bio and new_bio != instance.bio:
                instance.bio = new_bio

        if profile_pic_sent:
            new_profile_pic = validated_data.get('profile_pic')
            instance.profile_pic = new_profile_pic

        if cover_pic_sent:
            new_cover_pic = validated_data.get('cover_pic')
            instance.cover_pic = new_cover_pic

        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password1 = serializers.CharField(write_only=True, required=True)
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"error": "Old Password is Incorrect."})
        return value
    
    def validate_new_password(self, value):
        if self.new_password1 != self.new_password2:
            raise serializers.ValidationError({"error": "Password does not match."})
        if self.old_password == self.new_password1:
            raise serializers.ValidationError({"error": "New Password can not be the same as old Password."})
        return value

class PasswordResetSerializers(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError({"error": "User with this email does not exist."})
        return value
    
class PasswordResetConfirmSerializers(serializers.Serializer):
    token = serializers.CharField()
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        
        if not PasswordResetTokenGenerator().check_token(user, data['token']):
            raise serializers.ValidationError("Invalid or Expired Token")
        
        return data
    
class FollowSerializer(serializers.Serializer):
    username = serializers.CharField()