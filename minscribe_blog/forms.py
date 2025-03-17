from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, User, Comments, CognitiveProfile, PostTranslation

# A form for creating and updating user instances
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label=_('Password'))
    confirm_password = forms.CharField(widget=forms.PasswordInput, label=_('Confirm Password'))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile_picture', 'bio', 'preferred_language'] # fields to be included
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'profile_picture': _('Profile Picture'),
            'bio': _('Biography'),
            'preferred_language': _('Preferred Language'),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_("Passwords do not match"))
        return cleaned_data

# A form for creating and editing post objects
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'language'] # fields to be included
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': _('Write your post here...')
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter post title')
            })
        }
        labels = {
            'title': _('Title'),
            'content': _('Content'),
            'language': _('Language'),
        }

# Form for post translations
class PostTranslationForm(forms.ModelForm):
    class Meta:
        model = PostTranslation
        fields = ['language', 'title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
            })
        }
        labels = {
            'language': _('Language'),
            'title': _('Title'),
            'content': _('Content'),
        }

# A form for creating and editing comments       
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['content', 'language']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Write your comment here...')
            })
        }
        labels = {
            'content': _('Comment'),
            'language': _('Language'),
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
        labels = {
            'learning_style': _('Learning Style'),
            'interest_vectors': _('Interest Vectors'),
            'content_preferences': _('Content Preferences'),
            'cognitive_profile': _('Cognitive Profile'),
            'social_interactions': _('Social Interactions'),
        }

# A form for updating user profile details with the email being unique across users.
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture', 'bio', 'preferred_language'] # fields to be included
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'profile_picture': _('Profile Picture'),
            'bio': _('Biography'),
            'preferred_language': _('Preferred Language'),
        }
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.user_id
        if User.objects.filter(email=email).exclude(user_id=user_id).exists():
            raise forms.ValidationError(_("This email address is already in use."))
        return email

# A form for users to change their password, ensuring the new password meets requirements   
class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput, label=_('Current Password'))
    new_password = forms.CharField(widget=forms.PasswordInput, label=_('New Password'))
    confirm_new_password = forms.CharField(widget=forms.PasswordInput, label=_('Confirm New Password'))
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_new_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError(_("New passwords don't match"))
            if len(new_password) < 8:
                raise forms.ValidationError(_("New password must be at least 8 characters long"))
        return cleaned_data