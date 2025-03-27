from django.db import models
from ..minscribe_blog.models import User, Post
# Create your models here.
class ContentSuggestion(models.Model):
    suggestion_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    description = models.TextField()
    relevance_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return self.topic
    
class ContentAnalysis(models.Model):
    analysis_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    readability_score = models.FloatField()
    seo_score = models.FloatField()
    relevance_score = models.FloatField()
    keywords = models.JSONField()
    suggestions = models.TextField()
    
    def __str__(self):
        return f"Analysis for {self.post.title}"