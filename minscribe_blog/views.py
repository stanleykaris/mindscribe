from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction, models
from .models import Post, Poll, PollChoice, Quiz, QuizQuestion, User
from .forms import PostForm, UserForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from rest_framework.views import APIView
from .serializers import UserSerializer
from .exceptions import QuizSubmissionError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return Response({'message': 'Welcome to the Minscribe API!'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        # Hash password before saving
        serializer.validated_data['password'] = make_password(serializer.validated_data['password'])
        user = serializer.save()
        
        # Generating tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
 
@api_view(['POST']) 
@permission_classes([AllowAny])  
def register_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # Hash password before saving
            password = make_password(password)
            user = User(username=username, password=password)
            user.save()
            messages.success(request, 'User created successfully.')
            return redirect('login')
    else:
        form = UserForm()

    return render(request, 'blog/registration/register.html', {'form': form})

# Protected view
class PostView(APIView):
    permission_classes = [IsAuthenticated]
    def get_queryset(self, user=None):
        qs = Post.objects.all().published()
        if user and user.is_authenticated:
            user_posts = Post.objects.filter(user=user)
            qs = (qs | user_posts).distinct()
        return qs
    
    def post_list_view(self, request):
        try:
            posts = self.get_queryset(user=request.user)
            context = {
                'object_list': posts,
                'title': 'Blog Posts'
            }
            return render(request, 'blog/post_list.html', context)
        except Exception as e:
            # The `messages` in the Django code snippet provided is a part of Django's messaging
            # framework. It is used to display messages to users after certain actions are performed.
            # These messages can be used to provide feedback, notifications, or alerts to users based
            # on their interactions with the web application.
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('home')
    
    def post_detail_view(self, request, slug):
        try:
            post = get_object_or_404(Post, slug=slug)
            
            # Check if user has permission to view the post
            if not post.is_published and not request.user.is_staff:
                if not request.user.is_authenticated or post.user != request.user:
                    raise PermissionError("You do not have permission to view this post.")
            
            context = {
                'object': post,
                'title': post.title
            }
            return render(request, 'blog/post_detail.html', context)
        except Exception as e:
            messages.error(request, f"An error occurred loading post: {str(e)}")
            return redirect('blog:post_list')
    
    @staff_member_required
    def post_create_view(self, request):
        try:
            form = PostForm(request.POST or None, request.FILES or None)
            if request.method == 'POST' and form.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.save()
                messages.success(request, 'Post created successfully.')
                return redirect('blog:post_detail', slug=post.slug)
            
            context = {
                'form': form,
                'title': 'Create New Post'
            }
            return render(request, 'blog/form.html', context)
        except Exception as e:
            messages.error(request, f"An error occurred creating post: {str(e)}")
            return redirect('blog:post_list')
    
    @staff_member_required
    def post_update_view(self, request, slug):
        try:
            post = get_object_or_404(Post, slug=slug)
            
            # Checking if user has permission to update the post
            if not request.user.is_staff and post.user != request.user:
                raise PermissionError("You do not have permission to update this post.")
            
            form = PostForm(data=request.POST or None, files=request.FILES or None, instance=post)
            if request.method == 'POST' and form.is_valid():
                form.save()
                messages.success(request, 'Post updated successfully.')
                return redirect('blog:post_detail', slug=post.slug)
            
            context = {
                'form': form,
                'title': f'Update {post.title}'
            }
            return render(request, 'blog/form.html', context)
        except PermissionError as e:
            messages.error(request, str(e))
            return redirect('blog:post_list')
        except Exception as e:
            messages.error(request, f"An error occurred updating post: {str(e)}")
            return redirect('blog:post_list')
    
    @staff_member_required
    def post_delete_view(self, request, slug):
        try:
            post = get_object_or_404(Post, slug=slug)
            
            # Checking if user has permission to delete post
            if not request.user.is_staff and post.user != request.user:
                raise PermissionError("You do not have permission to delete this post.")
            
            if request.method == "POST":
                post.delete()
                messages.success(request, 'Post deleted successfully.')
                return redirect('blog:post_list')
            
            context = {
                'object': post,
                'title': 'Delete {post.title}'
            }
            return render(request, 'blog/post_delete.html', context)
        except PermissionError as e:
            messages.error(request, str(e))
            return redirect('blog:post_list')
        except Exception as e:
            messages.error(request, f"An error occurred deleting post: {str(e)}")
            return redirect('blog:post_list')

# Protected view
class PollView(APIView):
    permission_classes = [IsAuthenticated]
    def create_poll(self, request):
        if request.method != 'POST':
           return JsonResponse({
               'status': 'error',
               'message': 'Invalid request method'
           }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
           
        try:
            # Validating required fields
            required_fields = ['question', 'choices', 'end_date', 'post_id']
            for field in required_fields:
                if field not in request.data:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'{field} is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            # Creating poll with validated data
            poll_data = {
                'question': request.data['question'],
                'end_date': request.data['end_date'],
                'post_id': request.data['post_id'],
                'created_by': request.user.id
            }
            
            # Validate end data
            if timezone.datetime.strptime(poll_data['end_date'], '%Y-%m-%d').date() < timezone.now().date():
                return JsonResponse({
                    'status': 'error',
                    'message': 'End date must be in the future'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Create poll
            poll = Poll.objects.create(**poll_data)
            
            # Create poll choices
            choices = request.POST.getlist('choices')
            if not choices:
                poll.delete()
                return JsonResponse({
                    'status': 'error',
                    'message': 'At least one choice is required'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            poll_choices = [
                PollChoice(poll=poll, choice_text=choice)
                for choice in choices if choice.strip()
            ]
            PollChoice.objects.bulk_create(poll_choices)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Poll created successfully',
                'poll_id': poll.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def vote(self, request, poll_id):
        if request.method != 'POST':
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request method'
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            
        try:
            poll = get_object_or_404(Poll, pk=poll_id)
            
            # Check if poll has ended
            if poll.end_date < timezone.now().date():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Poll has ended'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Validate choice
            choice_id = request.POST.get('choice')
            if not choice_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid Choice'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                selected_choice = poll.pollchoice_set.get(pk=choice_id)
            except PollChoice.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid Choice'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Record vote
            selected_choice.votes += 1
            selected_choice.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Vote recorded successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Protected view
class QuizView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def create_quiz(self, request):
        if request.method == 'POST':
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request method'
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        try:
            quiz = get_object_or_404(Quiz, pk=request.POST['quiz_id'])
            
            # Validate choice submission
            choice_id = request.POST.get('choice')
            if not choice_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid Choice'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                selected_choice = quiz.quizchoice_set.get(pk=choice_id)
            except QuizQuestion.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid Choice'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Check if quiz has ended
            if quiz.end_date < timezone.now().date():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Quiz has ended'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # Record answer and check if correct
            if selected_choice.is_correct:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Correct answer'
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Incorrect answer'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Protected view
class QuizSubmissionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def validate_submission(self, quiz_id, choice_id):
        if not quiz_id or not choice_id:
            raise QuizSubmissionError(
                "Missing required parameters: quiz_id and choice_id",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            quiz = get_object_or_404(Quiz, pk=quiz_id)
            selected_choice = quiz.quizquestion_set.get(pk=choice_id).first()
            
            if not selected_choice:
                raise QuizSubmissionError(
                    "Invalid choice",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            return quiz, selected_choice
        
        except Quiz.DoesNotExist:
            raise QuizSubmissionError(
                "Invalid quiz",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    def check_quiz_availability(self, quiz):
        if quiz.end_date and quiz.end_date < timezone.now():
            raise QuizSubmissionError(
                "Quiz has ended",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        if not quiz.is_active:
            raise QuizSubmissionError(
                "Quiz is not active",
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    def process_submission(self, quiz, selected_choice, user):
        try:
            with transaction.atomic():
                # Record submission
                submission = quiz.submissions.create(
                    user=user,
                    choice=selected_choice,
                    submitted_dat=timezone.now()
                )
                
                # Update quiz statistics
                selected_choice.times_chosen = models.F('times_chosen') + 1
                selected_choice.save()
                
                response_data = {
                    'is_correct': selected_choice.is_correct,
                    'submission_id': submission.id,
                    'feedback': selected_choice.feedback or None
                }
                
                if selected_choice.is_correct:
                    response_data.update({
                        'message': 'Correct answer',
                        'status': 'success',
                        'points_earned': quiz.points
                    })
                else:
                    response_data.update({
                        'message': 'Incorrect answer',
                        'status': 'error',
                        'points_earned': 0
                    })
                    
                return response_data
            
        except Exception as e:
            raise QuizSubmissionError(
                f"Error processing submission: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def post(self, request, quiz_id):
        try:
            choice_id = request.data.get('choice') 
            if not choice_id:
                raise QuizSubmissionError(
                    "Missing choice_id",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            quiz, selected_choice = self.validate_submission(quiz_id, choice_id)
            self.check_quiz_availability(quiz)
            reponse_data = self.process_submission(quiz, selected_choice, request.user)
            
            return JsonResponse(reponse_data, status=status.HTTP_200_OK)
        
        except QuizSubmissionError as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=e.status_code)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        
        
