# Generated by Django 4.2.1 on 2023-06-20 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot_logic', '0006_rename_manualchat_chat_alter_chat_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailsupport',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
