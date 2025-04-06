from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from .models import User, Poll, PollChoice, QuizQuestion, Quiz, QuizSubmission, Comments, Post
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ( 'username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True}
            }
        
    def validate(self, data):
        # Password validation
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.set_password(validated_data['password'])
        
        for field in ['phone_number', 'profile_image']:
            if field in validated_data:
                setattr(user, field, validated_data[field])
                
        user.save()
        
        return user

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    email = serializers.EmailField(validators=[UniqueValidator(queryset=get_user_model().objects.all())])

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password']

    def validate(self, data):
        """Ensure username and email are unique."""
        if get_user_model().objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists.")
        if get_user_model().objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists.")
        return data

    def create(self, validated_data):
        """Create a new user with a hashed password."""
        validated_data['password'] = make_password(validated_data['password'])
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'publication_date', 'last_edited', 'likes', 'dislikes', 'views', 'comment_count', 'status', 'moderation_flagged', 'moderation_reason', 'ai_summary', 'ai_keywords', 'ai_sentiment', 'ai_translation', 'has_poll', 'has_quiz', 'has_livestream', 'collaborators', 'is_collaborative', 'version_history', 'created_at']
        read_only_fields = ['comment_count', 'version_history', 'created_at']
        
class AuthorProfileSerializer(serializers.ModelSerializer):
    total_posts = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture', 'bio', 'total_posts', 'total_likes', 'posts']
        read_only_fields = ['total_posts', 'total_likes', 'posts']
        
    def get_total_posts(self, obj):
        return Post.objects.filter(author=obj).count()
    
    def get_total_likes(self, obj):
        return Post.objects.filter(author=obj).aggregate(total_likes=Sum('likes'))['total_likes']
    
    def get_posts(self, obj):
        posts = Post.objects.filter(author=obj)
        return PostSerializer(posts, many=True).data
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)   
class PollChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollChoice
        fields = ['id', 'choice_text', 'votes']
        
class PollSerializer(serializers.ModelSerializer):
    choices = PollChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = ['id', 'question', 'choices', 'created_date', 'end_date', 'is_active']

    def create(self, validated_data):
        choices = validated_data.pop('choices', [])
        poll = Poll.objects.create(**validated_data)

        for choice_data in choices:
            PollChoice.objects.create(poll=poll, **choice_data)

        return poll
    
class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ['id', 'choice_text', 'is_correct']
        
class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'question', 'questions', 'created_date', 'end_date', 'is_active']

    def create(self, validated_data):
        questions = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions:
            QuizQuestion.objects.create(quiz=quiz, **question_data)

        return quiz

class QuizSubmissionSerializer(serializers.Serializer):
    class Meta:
        model = QuizSubmission
        fields = ['submission_id', 'quiz_id', 'choice', 'submission_date']
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ['id', 'post_id', 'author_id', 'content', 'publication_date', 'last_edited', 'likes', 'dislikes', 'moderation_flagged', 'moderation_reason']
        read_only_fields = ['publication_date', 'last_edited', 'likes', 'dislikes', 'moderation_flagged', 'moderation_reason']
