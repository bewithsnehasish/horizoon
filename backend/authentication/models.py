import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from backend.utils import aadhaar_regex, phone_regex

User = get_user_model()


class Client(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False,unique=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    authToken = models.UUIDField(default=uuid.uuid4, editable=False)
    createdAt = models.DateTimeField(auto_now_add=True, editable=False)
    updatedAt = models.DateTimeField(auto_now=True, editable=False)

    def save(self, *args, **kwargs):
        # Check if this is a new object (no id exists yet)
        if not self.id:
            # Check if a client with this username already exists
            if Client.objects.filter(email=self.email).exists():
                raise ValidationError(
                    f"A client with email '{self.email}' already exists."
                )

        # If validation passes, proceed with the normal save
        super(Client, self).save(*args, **kwargs)

    def __str__(self):
        return f"ID: {self.user_id}/ Username : {self.username} / Email: {self.email} / AuthToken : {self.authToken}"


class ClientDetails(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=100,
        validators=[phone_regex],
        unique=True,  # optional, if you want each phone to be unique
    )

    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    )
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)
    age = models.IntegerField(default=18)
    aadhaar = models.CharField(max_length=100, validators=[aadhaar_regex], unique=True)
    joinedAt = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"Name: {self.name} / Phone: {self.phone} / Gender: {self.gender}"

class Renter(models.Model):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False,unique=True)
    profile_pic = models.TextField(blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=100, unique=True)
    rating = models.PositiveIntegerField(default=0)
    address = models.TextField(blank=True)
    phone = models.CharField(
        max_length=100,
        validators=[phone_regex],
        unique=True
    )
    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    )
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)
    aadhaar = models.CharField(max_length=100, unique=True)
    joinedAt = models.DateTimeField(auto_now_add=True, editable=False)
    addedby = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  
        null=True,
        blank=True,
        related_name='renters_added'
    )
    verification_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Renter Full Name: {self.full_name}, Added By: {self.addedby}, Id: {self.user_id}"

    class Meta:
        ordering = ['-joinedAt']