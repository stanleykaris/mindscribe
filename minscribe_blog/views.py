from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
from .models import Post, Poll, PollChoice, Quiz, QuizQuestion
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework.views import APIView
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

# Create your views here.
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
    
class PostView(APIView):
    def post_list_view(self, request):
        qs = Post.objects.all().published()
        if request.user.is_authenticated:
            my_qs = Post.objects.filter(user=request.user)
            qs = (qs | my_qs).distinct()
        template_name = 'blog/post_list.html'
        context = {'object_list': qs}
        return render(request, template_name, context)
    
    def post_detail_view(self, request, slug):
        obj = get_object_or_404(Post, slug=slug)
        template_name = 'blog/post_detail.html'
        context = {"object": obj}
        return render(request, template_name, context)
    
    @staff_member_required
    def post_create_view(self, request):
        form = PostForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            form = PostForm()
        template_name = 'blog/form.html'
        context = {'form': form}
        return render(request, template_name, context)
    
    @staff_member_required
    def post_update_view(self, request, slug):
        obj = get_object_or_404(Post, slug=slug)
        form = PostForm(request.POST or None, instance=obj)
        if form.is_valid():
            form.save()
        template_name = 'blog/form.html'
        context = {'form': form, 'title': f"Update {obj.title}"}
        return render(request, template_name, context)
    
    def post_delete_view(self, request, slug):
        obj = get_object_or_404(Post, slug=slug)
        if request.method == "POST":
            obj.delete()
            return redirect("/blog")
        template_name = 'blog/post_delete.html'
        context = {'object': obj}
        return render(request, template_name, context)
        

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
        
    def submit_quiz(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        selected_choice = quiz.quizchoice_set.get(pk=request.POST['choice'])
        if selected_choice.is_correct:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Incorrect answer'})
        
