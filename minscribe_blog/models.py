from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.

def validate_image_size(value):
    filesize = value.size
    
    if filesize > 5 * 1024 * 1024:
        raise ValidationError(_("The maximum file size that can be uploaded is 5MB"))
    else:
        return value
class User(models.Model):
    user_id = models.AutoField(primary_key=True, null=False)
    username = models.CharField(max_length=100, null=False, unique=True)
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=100, null=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, validators=[validate_image_size], help_text=_("Maximum file size allowed is 5MB"))
    bio = models.TextField(blank=True)
    registration_date = models.DateTimeField(auto_now_add=True, null=False)
    last_login = models.DateTimeField(auto_now=True, null=False)
    preferred_language = models.CharField(max_length=10, choices=settings.LANGUAGES, default='en')
    
    def __str__(self):
        return self.username
    
    """
    The save method in the User model 
ensures old profile pictures are deleted when updated.
    """
    def save(self, *args, **kwargs):
        # Delete the old file when replacing by updating the file
        try:
            this = User.objects.get(user_id=self.user_id)
            if this.profile_picture != self.profile_picture:
                this.profile_picture.delete(save=False)
        except User.DoesNotExist:
            pass
        super(User, self).save(*args, **kwargs)
    
class Post(models.Model):
    post_id = models.AutoField(primary_key=True, null=False)
    author_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=200, null=False)
    content = models.TextField(null=False)
    publication_date = models.DateTimeField(auto_now_add=True, null=False)
    last_edited = models.DateTimeField(auto_now=True, null=False)
    likes = models.IntegerField(default=0, null=False)
    dislikes = models.IntegerField(default=0, null=False)
    views = models.IntegerField(default=0, null=False)
    comment_count = models.IntegerField(default=0, null=False)
    status = models.CharField(max_length=20, null=False)
    moderation_flagged = models.BooleanField(default=False, null=False)
    moderation_reason = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True)
    ai_keywords = models.TextField(blank=True)
    ai_sentiment = models.CharField(max_length=20, blank=True)
    ai_translation = models.TextField(blank=True)
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default='en')
    
    def __str__(self):
        return self.title
    
    def get_translation(self, language_code):
        try:
            return self.translations.get(language=language_code)
        except PostTranslation.DoesNotExist:
            return None

class PostTranslation(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    ai_summary = models.TextField(blank=True)
    ai_keywords = models.TextField(blank=True)
    ai_sentiment = models.CharField(max_length=20, blank=True)
    
    class Meta:
        unique_together = ('post', 'language')
        verbose_name = _('Post Translation')
        verbose_name_plural = _('Post Translations')
    
    def __str__(self):
        return f"{self.post.title} ({self.language})"

class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=50, unique=True, null=False)
    
    def __str__(self):
        return self.name
    
class TagTranslation(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    name = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ('tag', 'language')
        verbose_name = _('Tag Translation')
        verbose_name_plural = _('Tag Translations')
    
    def __str__(self):
        return f"{self.tag.name} ({self.language})"
    
class PostTag(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE, null=False)
    
    def __str__(self):
        return f"{self.post_id} - {self.tag_id}"
    
class Category(models.Model):
    category_id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=50, unique=True, null=False)

    def __str__(self):
        return self.name
    
class CategoryTranslation(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='translations')
    language = models.CharField(max_length=10, choices=settings.LANGUAGES)
    name = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ('category', 'language')
        verbose_name = _('Category Translation')
        verbose_name_plural = _('Category Translations')
    
    def __str__(self):
        return f"{self.category.name} ({self.language})"
    
class PostCategory(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"{self.post_id} - {self.category_id}"
    
class Comments(models.Model):
    comment_id = models.AutoField(primary_key=True, null=False)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    author_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    content = models.TextField(null=False)
    publication_date = models.DateTimeField(auto_now_add=True, null=False)
    last_edited = models.DateTimeField(auto_now=True, null=False)
    likes = models.IntegerField(default=0, null=False)
    dislikes = models.IntegerField(default=0, null=False)
    moderation_flagged = models.BooleanField(default=False, null=False)
    moderation_reason = models.TextField(blank=True)
    language = models.CharField(max_length=10, choices=settings.LANGUAGES, default='en')

    def __str__(self):
        return f"{self.author_id} - {self.post_id}"
    
class CognitiveProfile(models.Model):
    LEARNING_STYLE_CHOICES = [
        ('visual', _('Visual')),
        ('auditory', _('Auditory')),
        ('reading', _('Reading/Writing')),
        ('kinesthetic', _('Kinesthetic')),
    ]
    
    cognitive_profile_id = models.AutoField(primary_key=True, null=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    interest_vectors = models.JSONField(null=False)
    learning_style = models.CharField(max_length=50, null=False, choices=LEARNING_STYLE_CHOICES)
    content_preferences = models.JSONField(null=False)
    cognitive_profile = models.JSONField(null=False)
    social_interactions = models.JSONField(null=False)
    
    def __str__(self):
        return f"{self.user_id} - {self.learning_style}"
    
class Recommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True, null=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    recommendation_type = models.CharField(max_length=20, null=False)
    recommendation_date = models.DateTimeField(auto_now_add=True, null=False)
    recommendation_reason = models.TextField(blank=True)
    algorithm_used = models.CharField(max_length=50, null=False)
    
    def __str__(self):
        return f"{self.user_id} - {self.post_id}"