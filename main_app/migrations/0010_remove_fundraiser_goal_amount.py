# Generated by Django 5.0.3 on 2024-04-03 01:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0009_alter_fundraiser_goal_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fundraiser',
            name='goal_amount',
        ),
    ]
