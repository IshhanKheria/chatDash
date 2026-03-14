import re
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password_confirm')

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', value):
            raise serializers.ValidationError(
                'Username must be 3-30 characters, letters, numbers and underscores only.'
            )
        return value

    def validate_email(self, value):
        return value.lower().strip()

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters.')
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'\d', value):
            raise serializers.ValidationError('Password must contain at least one digit.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate_email(self, value):
        return value.lower().strip()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'bio', 'avatar', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, min_length=3, max_length=30)
    email = serializers.EmailField(required=False)
    bio = serializers.CharField(required=False, allow_blank=True, max_length=500)

    class Meta:
        model = User
        fields = ('username', 'email', 'bio', 'avatar')

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', value):
            raise serializers.ValidationError(
                'Username must be 3-30 characters, letters, numbers and underscores only.'
            )
        return value

    def validate_email(self, value):
        return value.lower().strip()
