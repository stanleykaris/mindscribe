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
    path('posts/<slug:slug>/', views.PostView.as_view(), name='post-detail'),
    path('posts/<slug:slug>/comments/', views.CommentView.as_view(), name='post-comments'),
    path('posts/<slug:slug>/comments/<int:comment_id>/', views.CommentView.as_view(), name='comment-detail'),
    path('posts/<slug:slug>/comments/<int:comment_id>/edit/', views.CommentView.as_view(), name='edit-comment'),
    path('posts/<slug:slug>/comments/<int:comment_id>/delete/', views.CommentView.as_view(), name='delete-comment'),
    path('posts/<slug:slug>/comments/create/', views.CommentView.as_view(), name='create-comment'),
    path('posts/<slug:slug>/comments/<int:comment_id>/like/', views.CommentView.as_view(), name='like-comment'),
    path('posts/<slug:slug>/comments/<int:comment_id>/dislike/', views.CommentView.as_view(), name='dislike-comment'),
    path('posts/<slug:slug>/comments/<int:comment_id>/reply/', views.CommentView.as_view(), name='reply-comment'),
    path('posts/<slug:slug>/comments/<int:comment_id>/reply/<int:reply_id>/', views.CommentView.as_view(), name='reply-detail'),
    path('posts/<slug:slug>/comments/<int:comment_id>/reply/<int:reply_id>/edit/', views.CommentView.as_view(), name='edit-reply'),
    path('posts/<slug:slug>/comments/<int:comment_id>/reply/<int:reply_id>/delete/', views.CommentView.as_view(), name='delete-reply'),
    path('posts/<slug:slug>/comments/<int:comment_id>/reply/create/', views.CommentView.as_view(), name='create-reply'),
    path('posts/<slug:slug>/comments/<int:comment_id>/reply/<int:reply_id>/like/', views.CommentView.as_view(), name='like-reply'),
    path('posts/<slug:slug>/comments/<int:comment_id>/reply/<int:reply_id>/dislike/', views.CommentView.as_view(), name='dislike-reply'),
    path('posts/<slug:slug>/comments/<int:comment_id>/reply/<int:reply_id>/report/', views.CommentView.as_view(), name='report-reply'),
    path('posts/<slug:slug>/collaborators/', views.CollaboratorView.as_view(), name='collaborator-list'),
    path('posts/<slug:slug>/collaborators/create/', views.CollaboratorView.as_view(), name='create-collaborator'),
    path('posts/<slug:slug>/collaborators/<int:collaborator_id>/', views.CollaboratorView.as_view(), name='collaborator-detail'),
    path('posts/<slug:slug>/collaborators/<int:collaborator_id>/edit/', views.CollaboratorView.as_view(), name='edit-collaborator'),
    path('posts/<slug:slug>/collaborators/<int:collaborator_id>/delete/', views.CollaboratorView.as_view(), name='delete-collaborator'),
    path('posts/<slug:slug>/collaborators/<int:collaborator_id>/like/', views.CollaboratorView.as_view(), name='like-collaborator'),
    path('posts/<slug:slug>/collaborators/<int:collaborator_id>/dislike/', views.CollaboratorView.as_view(), name='dislike-collaborator'),
    path('posts/<slug:slug>/collaborators/<int:collaborator_id>/report/', views.CollaboratorView.as_view(), name='report-collaborator'),
    path('posts/<slug:slug>/collaborators/<int:collaborator_id>/accept/', views.CollaboratorView.as_view(), name='accept-collaborator'),
    path('posts/<slug:slug>/collaborators/<int:collaborator_id>/reject/', views.CollaboratorView.as_view(), name='reject-collaborator'),
    path('posts/<slug:slug>/collaborators/<int:collaborator_id>/invite/', views.CollaboratorView.as_view(), name='invite-collaborator'),
    path('posts/<slug:slug>/collaborators/<int:collaborator_id>/invite/<int:invite_id>/', views.CollaboratorView.as_view(), name='invite-detail'),
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