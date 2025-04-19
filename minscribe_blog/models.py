from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from markdownify import markdownify as md
from tinymce.models import HTMLField
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
    content = HTMLField(null=False)
    markdown_content = models.TextField(blank=True)
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
    has_poll = models.BooleanField(default=False)
    has_quiz = models.BooleanField(default=False)
    has_livestream = models.BooleanField(default=False)
    collaborators = models.ManyToManyField(User, through='Collaboration', related_name='collaborative_posts')
    original_author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='original_posts')
    is_collaborative = models.BooleanField(default=False)
    version_history = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.markdown_content = md(self.content)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=50, unique=True, null=False)
    slug = models.SlugField(unique=True, null=False, default=name)
    
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
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return f"{self.author_id} - {self.post_id}"
    
class CognitiveProfile(models.Model):
    # Defining a lifestyle choice list
    LEARNING_STYLE_CHOICES = [
        ('Visual', 'Visual'),
        ('Auditory', 'Auditory'),
        ('Reading/Writing', 'Reading/Writing'),
        ('Kinesthetic', 'Kinesthetic'),
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
    
class Poll(models.Model):
    poll_id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    question = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.question
    
class PollChoice(models.Model):
    choice_id = models.AutoField(primary_key=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.choice_text
    
class Quiz(models.Model):
    quiz_id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    passing_score = models.IntegerField(default=70)
    
    def is_expired(self):
        """Checks if the quiz has expired"""
        return timezone.now() > self.end_date
    
class QuizQuestion(models.Model):
    question_id = models.AutoField(primary_key=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=200)
    points = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    
class LiveStream(models.Model):
    stream_id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    stream_url = models.URLField()
    scheduled_time = models.DateTimeField()
    is_live = models.BooleanField(default=False)
    stream_key = models.CharField(max_length=100)
    
class QuizSubmission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    choice = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, default=None)
    submission_date = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField()
    error_type = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ['user_id', 'quiz_id']
        
class CollaborationInvite(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired')
    ]
    
    ROLE_CHOICES = [
        ('editor', 'Editor'),
        ('reviewer', 'Reviewer'),
        ('contributor', 'Contributor')
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    inviter = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='inviter', null=True)
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitee')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        unique_together = ('post', 'invitee')
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
        
class Collaboration(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=CollaborationInvite.ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('post', 'user')
        
class CollaborationHistory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    
class VersionHistory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)
    version_number = models.IntegerField()
    
    def __str__(self):
        return f"Version {self.id} of {self.post.title} by {self.user.username} on {self.timestamp}"