from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def api_info(request):
    return JsonResponse({
        'name': 'ChatDash API',
        'version': '1.0.0',
        'endpoints': {
            'auth': {
                'register': 'POST /api/auth/register',
                'login': 'POST /api/auth/login',
                'me': 'GET /api/auth/me',
                'profile': 'PUT /api/auth/profile',
                'search': 'GET /api/auth/users/search?q=',
                'users': 'GET /api/auth/users',
                'online': 'GET /api/auth/users/online',
                'refresh': 'POST /api/auth/token/refresh',
            },
            'messages': {
                'history': 'GET /api/messages/history/<user_id>/',
                'edit': 'PUT /api/messages/<message_id>/',
                'delete': 'DELETE /api/messages/<message_id>/delete/',
            },
            'conversations': {
                'list': 'GET /api/conversations/',
            },
            'rooms': {
                'list_create': 'GET/POST /api/rooms/',
                'detail': 'GET /api/rooms/<room_id>/',
                'add_member': 'POST /api/rooms/<room_id>/members/',
                'remove_member': 'DELETE /api/rooms/<room_id>/members/<user_id>/',
                'messages': 'GET /api/rooms/<room_id>/messages/',
            },
            'websocket': 'ws://localhost:8000/ws/chat/?token=<access_token>',
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_info),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/messages/', include('apps.chat.urls.message_urls')),
    path('api/conversations/', include('apps.chat.urls.conversation_urls')),
    path('api/rooms/', include('apps.chat.urls.room_urls')),
]
