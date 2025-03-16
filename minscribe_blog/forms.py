from django import forms
from .models import Post, User, Comments, CognitiveProfile

# A form for creating and updating user instances
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile_picture', 'bio'] # fields to be included
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

# A form for creating and editing post objects
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content'] # fields to be included
        widget = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write your post here...'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title'
            })
        }

# A form for creating and editing comments       
class CommentForm(forms.ModelForm):
    class Meta:
        models = Comments
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...'
            })
        }
        labels = {
            'content': 'Comment'
        }

# A form for creating or updating cognitve profile instances
class CognitiveProfileForm(forms.ModelForm):
    class Meta:
        model = CognitiveProfile
        fields = ['learning_style', 'interest_vectors', 'content_preferences', 'cognitive_profile', 'social_interactions'] # fields to be included
        widgets = {
            'learning_style': forms.Select(choices=CognitiveProfile.LEARNING_STYLE_CHOICES),
            'interest_vectors': forms.Textarea(attrs={'class': 'form-control'}),
            'content_preferences': forms.Textarea(attrs={'class': 'form-control'}),
            'cognitive_profile': forms.Textarea(attrs={'class': 'form-control'}),
            'social_interactions': forms.Textarea(attrs={'class': 'form-control'})
        }

# A form for updating user profile details with the email being unique across users.
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture', 'bio'] # fields to be included
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.user_id
        if User.objects.filter(email=email).exclude(user_id=user_id).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

# A form for users to change their password, ensuring the new password meets requirements   
class PasswordChageForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_new_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("New passwords don't match")
            if len(new_password) < 8:
                raise forms.ValidationError("New password must be at least 8 characters long")
        return cleaned_data