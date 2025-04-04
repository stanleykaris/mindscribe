from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Post, User, Comments, CognitiveProfile, Poll, LiveStream, Quiz
import logging

logger = logging.getLogger(__name__)

def log_model_change(sender, instance, action, created=None):
    """Generic logging function for model changes"""
    model_name = sender.__name__
    instance_id = getattr(instance, f"{model_name.lower()}_id", None)
    
    if created is not None:
        action_type = "created" if created else "updated"
    else:
        action_type = action
    
    log_message = f"{model_name} {instance_id} was {action_type} at {timezone.now()}"
    logger.info(log_message)
    
# Post signals
@receiver([pre_save, post_save, pre_delete, post_delete], sender=Post)
def track_post_changes(sender, instance, **kwargs):
    if 'created' in kwargs:
        log_model_change(sender, instance, "save", kwargs.get('created'))
    elif kwargs.get('signal') == pre_delete:
        log_model_change(sender, instance, "about to be deleted")
    elif kwargs.get('signal') == post_delete:
        log_model_change(sender, instance, "deleted")
        
# User signals
@receiver([pre_save, post_save], sender=User)
def track_user_changes(sender, instance, **kwargs):
    created = kwargs.get('created', False)
    if created:
        logger.info(f"New user registered: {instance.username}")
    else:
        logger.info(f"User {instance.username} profile updated")
        
# Comments signals
@receiver([post_save], sender=Comments)
def track_comment_changes(sender, instance, created, **kwargs):
    if created:
        post = instance.post_id
        post.comment_count = Comments.objects.filter(post_id=post).count()
        post.save()
        logger.info(f"New comment added to post {post.post_id}")
        
# Cognitive Profile signals
@receiver([post_save], sender=CognitiveProfile)
def track_profile_changes(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    logger.info(f"Cognitive profile {action}: {instance.id}")
    
# Poll Signals
@receiver([post_save], sender=Poll)
def track_poll_changes(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New poll created: {instance.poll_id}")
    else:
        logger.info(f"Poll {instance.poll_id} updated")
        
# Quiz signals
@receiver([post_save], sender=Quiz)
def track_quiz_changes(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New quiz created: {instance.quiz_id}")
    else:
        logger.info(f"Quiz {instance.quiz_id} updated")
 
# LiveStream signals       
@receiver([post_save], sender=LiveStream)
def track_stream_changes(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New live stream created: {instance.stream_id}")
    else:
        if instance.is_live:
            logger.info(f"Live stream {instance.stream_id} started")
        else:
            logger.info(f"Live stream {instance.stream_id} updated")
            