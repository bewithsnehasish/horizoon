# Generated by Django 5.2.1 on 2025-05-19 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_renter_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='renter',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='renter',
            name='profile_pic',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='renter',
            name='rating',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
