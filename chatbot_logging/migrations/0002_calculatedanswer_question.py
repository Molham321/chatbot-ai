# Generated by Django 3.1 on 2020-09-20 09:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot_logic', '0002_insert_data'),
        ('chatbot_logging', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='calculatedanswer',
            name='question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='chatbot_logic.question'),
        ),
    ]
