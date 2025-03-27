from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'mindscribe_blog'

urlpatterns = [
    path('posts/', views.PostView.as_view(), name='post-list'),
    path('polls/create/', views.PollView.as_view(), name='create-poll'),
    path('polls/<int:poll_id>/vote/', views.PollView.as_view(), name='vote-poll'),
    path('quiz/create/', views.QuizView.as_view(), name='create-quiz'),
    path('quiz/<int:quiz_id>/submit/', views.QuizView.as_view(), name='submit-quiz')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)