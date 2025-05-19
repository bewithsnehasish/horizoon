import uuid

from django.core.exceptions import ValidationError
from django.db import models

from backend.utils import aadhaar_regex, phone_regex

# Create your models here.


class Client(models.Model):
    # name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100, blank=True)
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
        return f" Username : {self.username} / Email: {self.email} / AuthToken : {self.authToken}"


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


class DeliveryBoy(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    age = models.IntegerField(default=18)
    phone = models.CharField(max_length=100, validators=[phone_regex], unique=True)
    aadhaar = models.CharField(max_length=100, validators=[aadhaar_regex], unique=True)
    STATUS_CHOICES = (
        ("Married", "Married"),
        ("Single", "Single"),
        ("Divorced", "Divorced"),
        ("Widowed", "Widowed"),
        ("Separated", "Separated"),
    )
    marital_status = models.CharField(choices=STATUS_CHOICES, max_length=100)
    authToken = models.UUIDField(default=uuid.uuid4, editable=False)
    createdAt = models.DateTimeField(auto_now_add=True, editable=False)
    updatedAt = models.DateTimeField(auto_now=True, editable=False)

    def save(self, *args, **kwargs):
        # Check if this is a new object (no id exists yet)
        if not self.id:
            # Check if a client with this username already exists
            if DeliveryBoy.objects.filter(username=self.username).exists():
                raise ValidationError(
                    f"A client with username '{self.username}' already exists."
                )
        # If validation passes, proceed with the normal save
        super(DeliveryBoy, self).save(*args, **kwargs)

    def __str__(self):
        return f"Name: {self.name} / Username: {self.username} / Age {self.age} / Phone: {self.phone} / marital_status: {self.marital_status} / AuthToken: {self.authToken}"


class Admin(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)  # Should be hashed
    authToken = models.UUIDField(default=uuid.uuid4, editable=False)
    createdAt = models.DateTimeField(auto_now_add=True, editable=False)
    updatedAt = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f"Admin: {self.username}"
