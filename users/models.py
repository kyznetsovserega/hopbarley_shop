from django.db import models

from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = "profile",
    )
    phone =models.CharField(max_length=20,blank=True)
    city =models.CharField(max_length=100,blank=True)
    address =models.TextField(blank=True)
    date_of_birth =models.DateField(null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [ "-created_at"]

    def __str__(self):
        return f"Profile of {self.user.username}"
