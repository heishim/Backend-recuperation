# Generated by Django 3.1.7 on 2021-04-09 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_auto_20210408_1543'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichier',
            name='contenu',
            field=models.FileField(upload_to='media'),
        ),
    ]