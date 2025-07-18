from django.contrib import admin
from .models import Post, Comment, Image, Tag, BookMark

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 3

class ImageInline(admin.TabularInline):
    model = Image
    extra = 3
    fields = ['image']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'captionn', 'created_at', 'updated', 'likes_count', 'reposted')
    list_per_page = 20
    list_filter = ('user', 'created_at',)
    search_fields = ('user', 'caption',)
    fieldsets = (
        (None, {'fields': ('user', 'caption', 'likes', 'repost')}),
    )
    filter_horizontal = ()
    readonly_fields = ['created_at', 'likes_num']
    inlines = [CommentInline, ImageInline]

    def likes_count(self, obj):
        return obj.likes.count()
    
    def reposted(self, obj):
        if obj.repost:
            return True
        return False
    
    def captionn(self, obj):
        return obj.caption[:90]
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment','user', 'post', 'created_at')
    list_filter = ('post', 'user',)
    fieldsets = (
        (None, {'fields': ('user', 'post', 'comment')}),
    )
    readonly_fields = ('created_at',)
    list_per_page = 20

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('post', 'image_tag', 'image')
    list_filter = ('post',)
    list_per_page = 10
    
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('tag',)
    list_filter = ('tag',)
    list_per_page = 20

@admin.register(BookMark)
class BookMarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user')
    list_per_page = 20
    list_filter = ('post', 'user')