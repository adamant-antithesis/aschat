# Generated by Django 5.1.6 on 2025-03-08 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0002_chatinvitation'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmember',
            name='role',
            field=models.CharField(choices=[('admin', 'Administrator'), ('moderator', 'Moderator'), ('member', 'Member')], default='member', max_length=10),
        ),
    ]
