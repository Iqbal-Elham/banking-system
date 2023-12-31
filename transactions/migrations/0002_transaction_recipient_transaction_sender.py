# Generated by Django 4.2.3 on 2023-08-09 04:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_profile_photo'),
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='recipient',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='received_transactions', to='accounts.userbankaccount'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transaction',
            name='sender',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='sent_transactions', to='accounts.userbankaccount'),
            preserve_default=False,
        ),
    ]
