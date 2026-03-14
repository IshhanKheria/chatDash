#!/usr/bin/env python
"""Seed demo users and messages for testing."""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.chat.models import Message, Room, RoomMember

User = get_user_model()

def seed():
    print("Seeding demo data...")

    # Create demo users
    users_data = [
        {'username': 'alice', 'email': 'alice@demo.com', 'password': 'DemoPass123'},
        {'username': 'bob', 'email': 'bob@demo.com', 'password': 'DemoPass123'},
        {'username': 'carol', 'email': 'carol@demo.com', 'password': 'DemoPass123'},
    ]

    users = []
    for data in users_data:
        user, created = User.objects.get_or_create(
            email=data['email'],
            defaults={'username': data['username']}
        )
        if created:
            user.set_password(data['password'])
            user.save()
            print(f"  Created user: {user.username}")
        else:
            print(f"  User exists: {user.username}")
        users.append(user)

    alice, bob, carol = users

    # Create some DM messages
    messages = [
        (alice, bob, "Hey Bob! How are you?"),
        (bob, alice, "Hi Alice! Doing great, thanks!"),
        (alice, bob, "Great to hear! Want to chat more?"),
        (bob, alice, "Absolutely! This chat app is awesome."),
        (carol, alice, "Alice, did you see the new features?"),
        (alice, carol, "Yes! The real-time messaging works perfectly!"),
    ]

    for sender, receiver, content in messages:
        msg, created = Message.objects.get_or_create(
            sender=sender, receiver=receiver, content=content,
            defaults={}
        )
        if created:
            print(f"  Created message: {sender.username} -> {receiver.username}")

    # Create a demo room
    room, created = Room.objects.get_or_create(
        name='General',
        defaults={'creator': alice, 'description': 'General discussion room'}
    )
    if created:
        print(f"  Created room: {room.name}")
        for user in users:
            RoomMember.objects.get_or_create(room=room, user=user)

    # Add some room messages
    room_messages = [
        (alice, "Welcome to the General room everyone!"),
        (bob, "Thanks! Excited to be here."),
        (carol, "This group chat feature is great!"),
    ]
    for sender, content in room_messages:
        msg, created = Message.objects.get_or_create(
            sender=sender, room=room, content=content
        )
        if created:
            print(f"  Room message from {sender.username}")

    print("\nSeed complete!")
    print("Demo credentials:")
    for data in users_data:
        print(f"  Email: {data['email']}  Password: {data['password']}")

if __name__ == '__main__':
    seed()
