from django.shortcuts import render, redirect

def home(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        return redirect('replica:menu')  
    return render(request, 'login.html')

def chatbot(request):
    return render(request, 'chatbot.html')

def prediction(request):
    return render(request, 'prediction.html')

def menu(request):
    return render(request, 'menu.html')