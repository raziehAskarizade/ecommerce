# Generated by Django 4.0.6 on 2022-08-06 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_alter_orderitem_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listorder',
            name='user',
        ),
    ]