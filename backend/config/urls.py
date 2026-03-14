from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/messages/', include('apps.chat.urls.message_urls')),
    path('api/conversations/', include('apps.chat.urls.conversation_urls')),
    path('api/rooms/', include('apps.chat.urls.room_urls')),
]
