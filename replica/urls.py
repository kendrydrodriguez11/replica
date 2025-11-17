from django.urls import path
from . import views

app_name = 'replica'

urlpatterns = [
    # Ruta principal redirige al login
    path('', views.login_view, name='login'),
    
    # Menú principal (después del login)
    path('menu/', views.menu, name='menu'),
    
    # Chatbot
    path('chatbot/', views.chatbot, name='chatbot'),
    
    # Predicción
    path('prediction/', views.prediction, name='prediction'),
    
    # Logout
]