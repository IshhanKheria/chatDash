from django.urls import path
from apps.chat.views.message_views import message_history, edit_message, delete_message

urlpatterns = [
    path('history/<int:user_id>/', message_history, name='message-history'),
    path('<int:message_id>/', edit_message, name='message-edit'),
    path('<int:message_id>/delete/', delete_message, name='message-delete'),
]
