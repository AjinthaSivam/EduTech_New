from django.contrib import admin
from django.urls import path, include
from chat.views import chat_view
from chat.views import get_chat_history
from chat.views import end_conversation
from learner import views
import quiz.urls as quiz_urls
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('chat/', chat_view, name='chat'),
    path('api/end_conversation/', end_conversation, name='end_conversation'),
    path('api/chat/history', get_chat_history, name='get_chat_history'),
    path('api/register/', views.register_view, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view, name='token_refresh'),
    
    # Quiz-related endpoints
    path('quiz/', include(quiz_urls))
]
