from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'registration_date', 'last_login')
    search_fields = ('username', 'email')
    readonly_fields = ('registration_date', 'last_login')
    fieldsets = (
        ('Personal Info', {
            'fields': ('username', 'email', 'profile_picture', 'bio')
        }),
        ('Timestamps', {
            'fields': ('registration_date', 'last_login'),
            'classes': ('collapse',),
        }
        )
    )

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    readonly_fields = ('author_id', 'publication_date', 'status', 'views', 'last_edited', 'likes', 'dislikes')
    fields = ('title', 'content', 'status')
    list_display = ('title', 'content', 'status','publication_date','author_id', 'views')
    list_filter = ("status", "publication_date",)
    search_fields = ['title', 'content']
    actions = ['make_published']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author_id = request.user
        super().save_model(request, obj, form, change)
        
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(author_id=request.user)
        return qs

@admin.register(Comments)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'author_id', 'content', 'publication_date')
    list_filter = ('publication_date',)
    search_fields = ('content',)
    readonly_fields = ('publication_date', 'last_edited', 'likes', 'dislikes')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(PostTag)
class PostTagAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'tag_id')
    list_filter = ('tag_id',)
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    
@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'category_id')
    list_filter = ('category_id',)

@admin.register(CognitiveProfile)
class CognitiveProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'learning_style')
    list_filter = ('learning_style',)
    readonly_fields = ('user_id',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.user_id = request.user
        super().save_model(request, obj, form, change)
        
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(user_id=request.user)
        return qs
    