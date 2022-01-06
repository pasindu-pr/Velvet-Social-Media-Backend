# Generated by Django 4.0 on 2022-01-04 06:06

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_user_birthdate_alter_user_location_and_more'),
        ('socialmedia', '0007_alter_post_created_at_alter_post_location_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='core.user'),
        ),
        migrations.AlterField(
            model_name='like',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='core.user'),
        ),
        migrations.AlterField(
            model_name='post',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 4, 11, 36, 41, 389760)),
        ),
        migrations.AlterField(
            model_name='share',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shares', to='core.user'),
        ),
    ]
