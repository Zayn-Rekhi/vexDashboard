# Generated by Django 2.2.12 on 2020-05-17 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='thumb',
            field=models.ImageField(blank=True, default='default.png', upload_to=''),
        ),
    ]