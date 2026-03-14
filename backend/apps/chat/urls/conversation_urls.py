from django.urls import path
from apps.chat.views.conversation_views import conversation_list

urlpatterns = [
    path('', conversation_list, name='conversation-list'),
]
