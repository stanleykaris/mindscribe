from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'mindscribe_blog'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('login/', views.login_user, name='login'),
    path('posts/', views.PostView.as_view(), name='post-list'),
    path('polls/create/', views.PollView.as_view(), name='create-poll'),
    path('polls/<int:poll_id>/vote/', views.PollView.as_view(), name='vote-poll'),
    path('quiz/create/', views.QuizView.as_view(), name='create-quiz'),
    path('quiz/<int:quiz_id>/submit/', views.QuizView.as_view(), name='submit-quiz'),
    path('<slug:slug>/', views.PostView.as_view(), name='post_detail'),
    path('create/', views.PostView.as_view(), name='create_post'),
    path('edit/<slug:slug>/', views.PostView.as_view(), name='edit_post'),
    path('delete/<slug:slug>/', views.PostView.as_view(), name='delete_post'),
    path('polls/', views.PollView.as_view(), name='poll_list'),
    path('polls/<int:poll_id>/', views.PollView.as_view(), name='poll_detail'),
    path('quiz/<int:quiz_id>/', views.QuizView.as_view(), name='quiz_detail'),
    path('', views.home, name='home')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)