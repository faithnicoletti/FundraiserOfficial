# Generated by Django 5.0.3 on 2024-04-03 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0013_fundraiser_goal_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='total_donated',
        ),
        migrations.AlterField(
            model_name='fundraiser',
            name='goal_amount',
            field=models.DecimalField(decimal_places=2, default=1200.0, max_digits=10),
        ),
    ]