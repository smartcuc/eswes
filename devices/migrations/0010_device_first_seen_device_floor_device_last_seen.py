# devices/migrations/0010_device_lifecycle_and_floor.py

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0009_alter_home_mqtt_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='first_seen',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='device',
            name='floor',
            field=models.ForeignKey(
                to='devices.floor',
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL
            ),
        ),
        migrations.AddField(
            model_name='device',
            name='last_seen',
            field=models.DateTimeField(
                null=True,
                blank=True
            ),
        ),
    ]
