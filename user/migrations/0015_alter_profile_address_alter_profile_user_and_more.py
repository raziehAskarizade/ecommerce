# Generated by Django 4.0.6 on 2022-08-07 11:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_alter_profile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.address'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user_profile',
            field=models.ImageField(blank=True, null=True, upload_to=user.models.upload_to_profile),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user_signature',
            field=models.ImageField(blank=True, null=True, upload_to=user.models.upload_to_signature),
        ),
    ]
