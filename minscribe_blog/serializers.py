from rest_framework import serializers
from .models import User, Poll, PollChoice, QuizQuestion, Quiz, QuizSubmission

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'first_name', 'last_name', 'phone_number', 'profile_image')
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
        
        for field in ['first_name', 'last_name', 'phone_number', 'profile_image']:
            if field in validated_data:
                setattr(user, field, validated_data[field])
                
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

class QuizSubmissionSerializer(serializers.Serializer):
    class Meta:
        model = QuizSubmission
        fields = ['submission_id', 'quiz_id', 'choice', 'submission_date']