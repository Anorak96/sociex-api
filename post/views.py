from post.models import Post, Comment, BookMark
from post import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema
from itertools import chain
from user.models import User

@extend_schema(tags=["Post"])
class FeedView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.PostSerializer

    def get(self, request):
        user_= request.user
        user = User.objects.get(username="Darlingtin")
        following = [prof for prof in user.following.all()]
        my_post = user.user_post.all()
        
        posts = []
        qs = None

        for us in following:
            u_post = us.user_post.all()
            posts.append(u_post)
        
        posts.append(my_post)

        #=== sort and chain post query===
        if len(posts)>0:
            qs = sorted(chain(*posts), reverse=True, key=lambda post: post.created_at)

        serializer = serializers.PostSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(tags=["Post"])
class PostDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = serializers.PostSerializer

    def get(self, request, id):
        post = Post.objects.get(id=id)
        post.views += 1
        post.save()
        serializer = serializers.PostSerializer(post, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@extend_schema(tags=["Post"])     
class DeletePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            post = Post.objects.get(id=id)
            if post.user == request.user:
                post.delete()
                return Response({"success": "Post Deleted"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error:", "You dont have permission to delete this post."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error:", str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["Post"])     
class DeleteCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            comment = Comment.objects.get(id=id)
            if comment.user == request.user:
                comment.delete()
                return Response({"success": "Comment Deleted"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error:", "You don't have permission to delete this post."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error:", str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["Post"])     
class UpdatePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.UpdatePostSerializer

    def patch(self, request, id):
        try:
            post = Post.objects.get(id=id)
            if post.user == request.user:
                serializer = serializers.UpdatePostSerializer(post, data=request.data, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error:", "You dont have permission to update this post."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error:", str(e)}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["Post"])
class CreatePostView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CreatePostSerializer
    # parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = serializers.CreatePostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["Post"])
class RePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.RePostSerializer

    def post(self, request, *args, **kwargs):
        original_post_id = request.data.get("post_id")

        # Validate that the original post exists
        try:
            original_post = Post.objects.get(id=original_post_id)
        except Post.DoesNotExist:
            return Response({"detail": "Original post not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.RePostSerializer(data=request.data, context={'request': request, 'original_post': original_post })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["Post"])
class CreateCommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CreateCommentSerializer

    def post(self, request, *args, **kwargs):
        serializer = serializers.CreateCommentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=["Post"])
class LikeView(APIView): 
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        post_id = request.data.get("post_id")
        post = Post.objects.get(pk=post_id)
        user = request.user

        if user in post.likes.all():
            post.likes_num -= 1
            post.likes.remove(user)
            is_liked = False
            post.save()
            likes = post.likes.count()
        else:
            post.likes_num += 1
            post.likes.add(user)
            is_liked = True
            post.views += 1
            post.save()
            likes = post.likes.count()
        return Response({'isliked': is_liked, 'num_of_likes': post.likes.count()}, status=status.HTTP_201_CREATED)
    
@extend_schema(tags=["Post"])
class BookMarksView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.BookMarkSerializer

    def get(self, request):
        user = request.user
        bookmarks = BookMark.objects.filter(user=user).order_by('-added')
        serializer = serializers.BookMarkSerializer(bookmarks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@extend_schema(tags=["Post"])
class AddPostToBookMarkView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.AddPostToBookMarkSerializer

    def post(self, request):
        post_id = request.data.get("post_id")
        post = Post.objects.get(id=post_id)
        user = request.user

        if BookMark.objects.filter(user=user, post=post).exists():
            bookmark = BookMark.objects.get(user=user, post=post)
            bookmark.delete()
            return Response({'success': "Post removed from bookmark."}, status=status.HTTP_204_NO_CONTENT)
        else:
            bookmark = BookMark.objects.create(user=user, post=post)
            return Response({'success': "Post added to bookmark."}, status=status.HTTP_201_CREATED)

