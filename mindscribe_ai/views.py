from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .ai_service import AIContentService
from django.http import JsonResponse

# Create your views here.
class ContentAssistantView:
    ai_service = AIContentService()
    
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def get_topic_suggestion(self, request):
        user_interests = request.user.cognitive_profile.interest_vectors
        trending_topics = ContentAssistantView.ai_service.get_trending_topics(user_interests)
        
        suggestions = ContentAssistantView.ai_service.generate_topic_suggestions(user_interests, trending_topics)
        
        return JsonResponse({'suggestions': suggestions})
    
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def analyze_content(self, request):
        content = request.data.get('content', '')
        analysis = ContentAssistantView.ai_service.analyze_content(content)

        return JsonResponse({'analysis': analysis})
    
    @api_view(['POST'])
    @permission_classes([IsAuthenticated])
    def improve_content(self, request):
        content = request.data.get('content', '')
        style_guide = request.data.get('style_guide', 'default')
        
        improved_content = ContentAssistantView.ai_service.improve_content(content, style_guide)
        
        return JsonResponse({'improved_content': improved_content})