from rest_framework import serializers
from post.models import Post, Image, Comment, BookMark
from user.models import User
from django.utils.timesince import timesince
from datetime import timedelta
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'cover_pic', 'profile_pic')

class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('id', 'post', 'image')

class CommentSerializer(serializers.ModelSerializer):
    created = serializers.SerializerMethodField()
    user = UserSerializer()
    
    def get_created(self, obj):
        now = timezone.now()
        delta = now - obj.created_at

        if delta < timedelta(days=1):
            return timesince(obj.created_at) + ' ago'
        else:
            return obj.created_at.strftime('%b %d, %Y %I:%M %p')

    class Meta:
        model = Comment
        fields = ('id', 'user', 'comment', 'post', 'created')

class PostSerializer(serializers.ModelSerializer):
    comment_post = CommentSerializer(many=True)
    user = UserSerializer()
    repost = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(), required=False, allow_null=True)
    reposted_post = serializers.SerializerMethodField()
    reposted_by = serializers.SerializerMethodField()
    likes = UserSerializer(many=True)
    post_images = serializers.SerializerMethodField()
    likes_num = serializers.SerializerMethodField()
    comment_num = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    is_reposted = serializers.SerializerMethodField()

    def get_updated_at(self, obj):
        now = timezone.now()
        delta = now - obj.updated

        if delta < timedelta(days=1):
            return timesince(obj.updated) + ' ago'
        else:
            return obj.updated.strftime('%b %d, %Y %I:%M %p')

    def get_created(self, obj):
        now = timezone.now()
        delta = now - obj.created_at

        if delta < timedelta(days=1):
            return timesince(obj.created_at) + ' ago'
        else:
            return obj.created_at.strftime('%b %d, %Y %I:%M %p')

    def get_post_images(self, obj):
        images = Image.objects.filter(post=obj)
        if images:
            return ImageSerializer(images, many=True).data
        
    def get_likes_num(self, obj):
        return obj.likes.count()

    def get_comment_num(self, obj):
        return obj.comment_post.count()

    def get_is_liked(self, obj):
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            user = request.user
            return obj.likes.filter(username=user.username).exists()
        return False
    
    def get_is_reposted(self, obj):
        if obj.repost:
            return True
        return False

    def get_reposted_post(self, obj):
        if obj.repost:
            return PostSerializer(obj.repost).data
        return None
    
    def get_reposted_by(self, obj):
        if obj.repost:
            return obj.user.username
        return None
    
    class Meta:
        model = Post
        fields = ('id', 'user', 'caption', 'likes', 'created', 'updated_at', 'likes_num', 'comment_post', 'comment_num', 'views', 
                'is_liked', 'post_images', 'repost', 'reposted_post', 'reposted_by', 'is_reposted')
        extra_kwargs = {'id': {'read_only': True}, 'created': {'read_only': True}}
        read_only_fields = ['reposted_post', 'likes_num', 'reposted_by']

class UpdatePostSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), allow_null=True, required=False)
    caption = serializers.CharField(required=False)

    class Meta:
        model = Post
        fields = ('id', 'caption', 'images')

    def validate(self, data):
        request = self.context.get('request')
        data["caption_sent"] = "caption" in request.data
        data["images_sent"] = "images" in request.data
        return data

    def update(self, instance, validated_data):
        caption_sent = validated_data.pop("caption_sent", False)
        images_sent = validated_data.pop("images_sent", False)

        if caption_sent:
            new_caption = validated_data.get('caption')
            if new_caption and new_caption != instance.caption:
                instance.caption = new_caption

        if images_sent:
            new_images = validated_data.get('images', [])
            instance.post_images.all().delete()
            for image in new_images:
                Image.objects.create(post=instance, image=image)

        instance.save()
        return instance

class CreatePostSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), required=False)
    caption = serializers.CharField(required=False)

    class Meta:
        model = Post
        fields = ('id', 'caption', 'images')

    def validate(self, data):
        request = self.context.get('request')
        data["caption_sent"] = "caption" in request.data
        data["images_sent"] = "images" in request.data
        return data

    def create(self, validated_data):
        # user_ = self.context['request'].user
        user = User.objects.get(username="Darlingtin")
        caption_sent = validated_data.pop("caption_sent", False)
        images_sent = validated_data.pop("images_sent", False)
        caption = validated_data.get("caption", "")
        images_ = validated_data.pop('images', [])
        print(caption, images_)
        post = Post.objects.create(
            user = user,
            caption = caption,
        )

        if images_:
            for image in images_:
                image = Image.objects.create(post=post, image=image)

        return post

class RePostSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), required=False)
    caption = serializers.CharField(required=False)

    class Meta:
        model = Post
        fields = ('id', 'caption', 'images')

    def validate(self, data):
        request = self.context.get('request')
        data["caption_sent"] = "caption" in request.data
        data["images_sent"] = "images" in request.data
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        repost = self.context['original_post']
        caption_sent = validated_data.pop("caption_sent", False)
        images_sent = validated_data.pop("images_sent", False)
        caption = validated_data.get("caption", "")
        images_ = validated_data.pop('images', [])
        post = Post.objects.create(
            user = user,
            caption = caption,
            repost=repost
        )

        if images_:
            for image in images_:
                image = Image.objects.create(post=post, image=image)
        return post

class CreateCommentSerializer(serializers.ModelSerializer):
    comment = serializers.CharField()
    post_id = serializers.IntegerField()
    
    class Meta:
        model = Comment
        fields = ('id', 'comment', 'post_id')

    def create(self, validated_data):
        user = self.context['request'].user
        post_id = validated_data["post_id"]
        post = Post.objects.get(id=post_id)

        comment = Comment.objects.create(
            user = user, 
            post = post,
            comment = validated_data['comment']
        )
        return comment

class BookMarkSerializer(serializers.ModelSerializer):
    post = PostSerializer()

    class Meta:
        model = BookMark
        fields = ('id', 'user', 'post', 'added')
        read_only_fields = ['user', 'added']

class AddPostToBookMarkSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
