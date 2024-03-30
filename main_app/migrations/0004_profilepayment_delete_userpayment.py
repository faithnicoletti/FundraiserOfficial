# Generated by Django 5.0.3 on 2024-03-30 21:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_userpayment'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfilePayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_bool', models.BooleanField(default=False)),
                ('stripe_checkout_id', models.CharField(max_length=500)),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main_app.profile')),
            ],
        ),
        migrations.DeleteModel(
            name='UserPayment',
        ),
    ]