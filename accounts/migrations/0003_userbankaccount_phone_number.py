# Generated by Django 4.2.3 on 2023-08-10 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_profile_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbankaccount',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]