from django.contrib import admin
from .models import (
    User, Post, Tag, PostTag, Category, PostCategory, 
    Comments, CognitiveProfile, Recommendation,
    PostTranslation, TagTranslation, CategoryTranslation
)

# Register your models here.

class PostTranslationInline(admin.TabularInline):
    model = PostTranslation
    extra = 1

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_id', 'publication_date', 'language', 'status')
    list_filter = ('status', 'language', 'publication_date')
    search_fields = ('title', 'content')
    inlines = [PostTranslationInline]

class TagTranslationInline(admin.TabularInline):
    model = TagTranslation
    extra = 1

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [TagTranslationInline]

class CategoryTranslationInline(admin.TabularInline):
    model = CategoryTranslation
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [CategoryTranslationInline]

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'registration_date', 'preferred_language')
    list_filter = ('registration_date', 'preferred_language')
    search_fields = ('username', 'email')

@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('author_id', 'post_id', 'publication_date', 'language')
    list_filter = ('publication_date', 'language')
    search_fields = ('content',)

@admin.register(CognitiveProfile)
class CognitiveProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'learning_style')
    list_filter = ('learning_style',)

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'post_id', 'recommendation_type', 'recommendation_date')
    list_filter = ('recommendation_type', 'recommendation_date')

# Register the many-to-many relationship models
admin.site.register(PostTag)
admin.site.register(PostCategory)