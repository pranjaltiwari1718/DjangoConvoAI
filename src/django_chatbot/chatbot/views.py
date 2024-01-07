from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai 
from openai import OpenAI
import os
from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone

#API_KEY = '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'
#OPENAI_API_KEY = API_KEY

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="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",
)

def ask_openai(message):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    
    answer = response.choices[0].message.content.strip()
    
    # Wrap the code response in a code panel
    formatted_answer = f'<div style="background-color: #f2f2f2; padding: 10px; border-radius: 5px;"><pre>{answer}</pre></div>'
    return formatted_answer

def chatbot(request):
    chats = Chat.objects.filter(user=request.user.id)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    
    return render(request, 'chatbot.html', {'chats': chats})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')