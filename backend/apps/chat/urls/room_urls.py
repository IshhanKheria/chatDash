from django.urls import path
from apps.chat.views.room_views import rooms, room_detail, add_member, remove_member, room_messages

urlpatterns = [
    path('', rooms, name='rooms'),
    path('<int:room_id>/', room_detail, name='room-detail'),
    path('<int:room_id>/members/', add_member, name='room-add-member'),
    path('<int:room_id>/members/<int:user_id>/', remove_member, name='room-remove-member'),
    path('<int:room_id>/messages/', room_messages, name='room-messages'),
]
