from django.db import models
from django.utils import timezone

from .role import Role
from apps.core.models import BaseModel
from django.contrib.postgres.fields import ArrayField
from .user import User
from .user_role import UserRole


class Invitation(BaseModel):
    """
    User invitation model for inviting users to join the organization.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]

    email = models.EmailField()
    role_ids = ArrayField(models.UUIDField(), default=list)
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_invitations'
    )
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='accepted_invitations'
    )
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'invitations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['token']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Invitation for {self.email}"

    @property
    def is_expired(self):
        """Check if invitation has expired."""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if invitation is valid."""
        return self.status == 'pending' and not self.is_expired

    def expire(self):
        """Mark invitation as expired."""
        self.status = 'expired'
        self.save()

    def revoke(self):
        """Revoke the invitation."""
        self.status = 'revoked'
        self.save()

    def accept(self, user):
        """Accept the invitation."""
        if not self.is_valid:
            raise ValueError("Invitation is not valid")

        self.status = 'accepted'
        self.accepted_by = user
        self.accepted_at = timezone.now()
        self.save()

        # Assign roles to user
        roles = Role.objects.filter(id__in=self.role_ids)
        for role in roles:
            UserRole.objects.get_or_create(
                user=user,
                role=role,
                defaults={'assigned_by': self.invited_by}
            )

        return user
