from django.db import migrations, connection
import os

import_path = './admin_panel/sql/'


def load_data_from_sql(file):
    sql = open(import_path + file, encoding='utf8').read()

    sql_statements = sql.split(';')

    for sql_statement in sql_statements:
        if sql_statement:
            with connection.cursor() as c:
                try:
                    c.execute(sql_statement)
                except:
                    print(f"Failed executing statement {sql_statement}")


def insert_data(apps, schema_editor):
    sql_files = os.listdir(import_path)

    for file in sql_files:
        load_data_from_sql(file)


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0006_adminsettings_mail_cancel_text'),
    ]

    operations = [
        migrations.RunPython(insert_data),
    ]
