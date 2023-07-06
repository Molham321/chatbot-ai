# Generated by Django 3.1 on 2020-09-13 09:06

from chatbot_logic.models import Answer, Context, Keyword, Question
from django.db import migrations, connection, models
from django.db.utils import OperationalError, IntegrityError
import os

import_path = './chatbot_logic/sql/'


def load_data_from_sql(file):
    sql = open(import_path + file, encoding='utf8').read()

    sql_statements = sql.split(';')

    for sql_statement in sql_statements:
        if sql_statement:
            with connection.cursor() as c:
                try:
                    c.execute(sql_statement)
                except OperationalError as err:
                    print(f"OperationalError: Failed executing statement {sql_statement}: {err}")
                except IntegrityError as err:
                    print(f"IntegrityError: Failed executing statement {sql_statement}: {err}")


def truncate_all(apps, schema_editor):
    answers = apps.get_model('chatbot_logic', 'answer')
    contexts = apps.get_model('chatbot_logic', 'context')
    keywords = apps.get_model('chatbot_logic', 'keyword')
    questions = apps.get_model('chatbot_logic', 'question')

    answers.objects.all().delete()
    contexts.objects.all().delete()
    keywords.objects.all().delete()
    questions.objects.all().delete()


def insert_data(apps, schema_editor):
    sql_files = os.listdir(import_path)
    sql_files.sort()

    for file in sql_files:
        print(f"importing sql file {file}")
        load_data_from_sql(file)


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot_logic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='question',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(truncate_all),
        migrations.RunPython(insert_data),
    ]
