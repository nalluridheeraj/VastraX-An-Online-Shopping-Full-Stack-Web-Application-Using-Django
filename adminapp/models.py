from django.db import models


class AdminUser(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    otp = models.CharField(max_length=10, blank=True, null=True)
    is_manager = models.BooleanField(default=False)  # True = manager, False = admin
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
