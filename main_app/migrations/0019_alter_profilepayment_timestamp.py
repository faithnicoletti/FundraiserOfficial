# Generated by Django 5.0.4 on 2024-05-02 17:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0018_delete_fundraiser_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilepayment',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
