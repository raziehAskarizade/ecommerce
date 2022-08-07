# Generated by Django 4.0.6 on 2022-08-03 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='picture',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='tax',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='title',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='id_product',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]