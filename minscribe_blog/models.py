from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.

def validate_image_size(value):
    filesize = value.size
    
    if filesize > 5 * 1024 * 1024:
        raise ValidationError("The maximum file size that can be uploaded is 5MB")
    else:
        return value
class User(models.Model):
    user_id = models.AutoField(primary_key=True, null=False)
    username = models.CharField(max_length=100, null=False, unique=True)
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=100, null=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, validators=[validate_image_size], help_text="Maximum file size allowed is 5MB")
    bio = models.TextField(blank=True)
    registration_date = models.DateTimeField(auto_now_add=True, null=False)
    last_login = models.DateTimeField(auto_now=True, null=False)
    
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
    
    def __str__(self):
        return self.title

class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=50, unique=True, null=False)
    
    def __str__(self):
        return self.name
    
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

    def __str__(self):
        return f"{self.author_id} - {self.post_id}"
    
class CognitiveProfile(models.Model):
    cognitive_profile_id = models.AutoField(primary_key=True, null=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    interest_vectors = models.JSONField(null=False)
    learning_style = models.CharField(max_length=50, null=False)
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