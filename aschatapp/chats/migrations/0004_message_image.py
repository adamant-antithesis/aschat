# Generated by Django 5.1.6 on 2025-03-18 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0003_chatmember_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='chat_images/'),
        ),
    ]
