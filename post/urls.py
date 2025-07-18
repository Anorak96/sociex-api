from django.urls import path
from . import views

app_name = 'post_api'
urlpatterns = [
    path('feeds', views.FeedView.as_view(), name='feed'),

    path('post/<int:id>', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:id>/delete/', views.DeletePostView.as_view(), name='delete_post'),
    path('post/<int:id>/update/', views.UpdatePostView.as_view(), name='update_post'),
    path('post/create/', views.CreatePostView.as_view(), name='create_post'),
    path('post/like/', views.LikeView.as_view(), name='like_post'),
    path('post/repost/', views.RePostView.as_view(), name='repost'),

    path('comment/create/', views.CreateCommentView.as_view(), name='create_comment'),
    path('comment/<int:id>/delete/', views.DeleteCommentView.as_view(), name='delete_comment'),

    path('bookmarks', views.BookMarksView.as_view(), name='bookmarks'),
    path('bookmark/create/', views.AddPostToBookMarkView.as_view(), name='add_post_to_bookmark'),
]
