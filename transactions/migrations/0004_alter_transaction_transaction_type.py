# Generated by Django 4.2.3 on 2023-08-10 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0003_remove_transaction_recipient_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Deposit'), (2, 'Withdrawal'), (3, 'Transfered'), (4, 'Received')]),
        ),
    ]
