# Generated by Django 5.2.1 on 2025-05-19 19:56

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_client_user_id_alter_renter_addedby'),
    ]

    operations = [
        migrations.AddField(
            model_name='renter',
            name='user_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
