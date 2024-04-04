# Generated by Django 5.0.3 on 2024-04-03 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0015_profile_total_amount_donated'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='content',
        ),
        migrations.AlterField(
            model_name='fundraiser',
            name='goal_amount',
            field=models.DecimalField(decimal_places=2, default=2000.0, max_digits=10),
        ),
    ]