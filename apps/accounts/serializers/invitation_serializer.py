"""
Invitation serializers.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from datetime import datetime, timedelta

from ..models import User, Role, Invitation
from apps.core.utils import generate_invitation_token
from .role_serializer import RoleSerializer


class InvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for Invitation model.
    """
    roles = RoleSerializer(source='role_ids', many=True, read_only=True)
    invited_by_name = serializers.CharField(source='invited_by.full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    is_valid = serializers.ReadOnlyField()
    
    class Meta:
        model = Invitation
        fields = [
            'id', 'email', 'role_ids', 'roles', 'token', 'expires_at',
            'status', 'invited_by_name', 'is_expired', 'is_valid',
            'created_at', 'accepted_at'
        ]
        read_only_fields = [
            'id', 'token', 'expires_at', 'status', 'invited_by_name',
            'is_expired', 'is_valid', 'created_at', 'accepted_at'
        ]


class InvitationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating invitations.
    """
    email = serializers.EmailField()
    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    
    def validate_email(self, value):
        """
        Validate email doesn't already exist as user.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email already exists."
            )
        
        return value
    
    def validate_role_ids(self, value):
        """
        Validate role IDs exist.
        """
        roles = Role.objects.filter(id__in=value)
        if len(roles) != len(value):
            raise serializers.ValidationError('Some role IDs are invalid.')
        
        return value
    
    def create(self, validated_data):
        """
        Create invitation.
        """
        request = self.context.get('request')
        
        # Generate invitation token
        token = generate_invitation_token(
            validated_data['email'],
            [str(role_id) for role_id in validated_data['role_ids']]
        )
        
        # Create invitation
        invitation = Invitation.objects.create(
            email=validated_data['email'],
            role_ids=validated_data['role_ids'],
            token=token,
            expires_at=datetime.now() + timedelta(days=7),
            invited_by=request.user
        )
        
        return invitation


class AcceptInvitationSerializer(serializers.Serializer):
    """
    Serializer for accepting invitations.
    """
    token = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """
        Validate invitation acceptance.
        """
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        
        # Validate invitation token
        try:
            from apps.core.utils import decode_jwt_token
            payload = decode_jwt_token(data['token'])
            
            if payload.get('type') != 'invitation':
                raise serializers.ValidationError("Invalid invitation token.")
            
            # Check if invitation exists and is valid
            invitation = Invitation.objects.filter(
                token=data['token'],
                status='pending'
            ).first()
            
            if not invitation:
                raise serializers.ValidationError("Invalid or expired invitation.")
            
            if invitation.is_expired:
                raise serializers.ValidationError("Invitation has expired.")
            
            data['invitation'] = invitation
            return data
            
        except Exception as e:
            raise serializers.ValidationError("Invalid invitation token.")
    
    def create(self, validated_data):
        """
        Create user from invitation.
        """
        invitation = validated_data['invitation']
        
        # Create user
        user = User.objects.create_user(
            email=invitation.email,
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        
        # Assign roles
        roles = Role.objects.filter(id__in=invitation.role_ids)
        user.roles.set(roles)
        
        # Update invitation
        invitation.status = 'accepted'
        invitation.accepted_at = datetime.now()
        invitation.save()
        
        return user


class AssignRoleSerializer(serializers.Serializer):
    """
    Serializer for assigning roles to users.
    """
    user_id = serializers.UUIDField()
    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1
    )
    
    def validate_user_id(self, value):
        """
        Validate user exists.
        """
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found.")
        return value
    
    def validate_role_ids(self, value):
        """
        Validate role IDs exist.
        """
        roles = Role.objects.filter(id__in=value)
        if len(roles) != len(value):
            raise serializers.ValidationError('Some role IDs are invalid.')
        return value
    
    def create(self, validated_data):
        """
        Assign roles to user.
        """
        user = User.objects.get(id=validated_data['user_id'])
        roles = Role.objects.filter(id__in=validated_data['role_ids'])
        
        # Add roles to user
        user.roles.add(*roles)
        
        return user
