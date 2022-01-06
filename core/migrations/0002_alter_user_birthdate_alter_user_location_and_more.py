# Generated by Django 4.0 on 2022-01-02 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='birthdate',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='location',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.URLField(null=True),
        ),
    ]
