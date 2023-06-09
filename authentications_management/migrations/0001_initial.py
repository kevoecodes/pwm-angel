# Generated by Django 4.2.2 on 2023-06-07 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NewUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobileNo', models.CharField(max_length=100)),
                ('accountNo', models.CharField(default=None, max_length=256)),
                ('first_name', models.CharField(default=None, max_length=100)),
                ('last_name', models.CharField(default=None, max_length=100)),
                ('email', models.CharField(default=None, max_length=100)),
                ('deviceNo', models.CharField(default=None, max_length=100)),
            ],
        ),
    ]
