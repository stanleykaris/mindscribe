from django.urls import path
from .views import ContentAssistantView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('ai/suggestions/', ContentAssistantView.get_topic_suggestion, name='topic-suggestions'),
    path('ai/analyze/', ContentAssistantView.analyze_content, name='analyze-content'),
    path('ai/improve/', ContentAssistantView.improve_content, name='improve-content'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)