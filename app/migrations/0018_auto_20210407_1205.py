# Generated by Django 3.1.7 on 2021-04-07 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_auto_20210407_1139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fichier',
            name='sortie',
        ),
        migrations.AddField(
            model_name='fichier',
            name='sorti',
            field=models.ImageField(default=1, upload_to=''),
            preserve_default=False,
        ),
    ]
