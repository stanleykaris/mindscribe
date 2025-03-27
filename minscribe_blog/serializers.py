from rest_framework import serializers
from .models import User, Poll, PollChoice, QuizQuestion, Quiz

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'profile_image', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login', 'groups', 'user_permissions')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
            profile_image=validated_data['profile_image']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
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
