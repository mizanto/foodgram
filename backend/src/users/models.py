from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Subscription(models.Model):
    """
    Model representing a user's subscription to another user.

    Fields::
    - user: The user who is following another user.
    - following: The user who is being followed by another user.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers'
    )

    class Meta:
        unique_together = ('user', 'following')
