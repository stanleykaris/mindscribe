from django.shortcuts import render, redirect
from django.utils import translation
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib import messages

# Create your views here.

def set_language(request):
    if request.method == 'POST':
        language = request.POST.get('language', settings.LANGUAGE_CODE)
        translation.activate(language)
        response = HttpResponseRedirect(request.POST.get('next', '/'))
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
        
        # If user is authenticated, update their preferred language
        if request.user.is_authenticated:
            request.user.preferred_language = language
            request.user.save()
            
        messages.success(request, _('Language changed successfully.'))
        return response
    return redirect('home')  # Redirect to home if not a POST request