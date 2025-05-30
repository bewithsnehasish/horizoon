# Generated by Django 5.2.1 on 2025-05-19 12:43

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="clientdetails",
            name="aadhaar",
            field=models.CharField(
                default=1,
                max_length=100,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        code="invalid_aadhaar",
                        message="Aadhaar number must be 12 digits long, should not start with 0 or 1, and should not contain any spaces or special characters",
                        regex="^[2-9]{1}[0-9]{3}[0-9]{4}[0-9]{4}$",
                    )
                ],
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="clientdetails",
            name="joinedAt",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
