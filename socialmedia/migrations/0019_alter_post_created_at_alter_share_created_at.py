# Generated by Django 4.0.1 on 2022-01-08 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0018_share_created_at_alter_post_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='share',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]