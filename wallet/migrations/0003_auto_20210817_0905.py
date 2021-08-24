# Generated by Django 3.2.6 on 2021-08-17 16:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_auto_20210816_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallettransaction',
            name='destination',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='destination', to='wallet.wallet'),
        ),
        migrations.AlterField(
            model_name='wallettransaction',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='source', to='wallet.wallet'),
        ),
    ]
