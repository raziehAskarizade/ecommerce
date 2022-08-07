# Generated by Django 4.0.6 on 2022-08-05 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_remove_phoneotp_forgot_remove_phoneotp_forgot_logged_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='phoneotp',
            name='validated',
            field=models.BooleanField(default=False, help_text='If it is True, that means user have validate otp successfully in second API'),
        ),
    ]
