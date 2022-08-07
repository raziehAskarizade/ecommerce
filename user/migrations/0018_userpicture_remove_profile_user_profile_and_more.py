# Generated by Django 4.0.6 on 2022-08-07 20:46

from django.db import migrations, models
import django.db.models.deletion
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_alter_profile_user_profile_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPicture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_profile', models.ImageField(blank=True, null=True, upload_to=user.models.upload_to_profile)),
                ('user_signature', models.ImageField(blank=True, null=True, upload_to=user.models.upload_to_signature)),
            ],
        ),
        migrations.RemoveField(
            model_name='profile',
            name='user_profile',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='user_signature',
        ),
        migrations.AddField(
            model_name='profile',
            name='pictures',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.userpicture'),
        ),
    ]