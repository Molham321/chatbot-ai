# Generated by Django 4.2.1 on 2023-07-01 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0005_adminsettings_mail_input_text_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminsettings',
            name='mail_cancel_text',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
