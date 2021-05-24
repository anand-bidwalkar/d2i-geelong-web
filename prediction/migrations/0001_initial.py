# Generated by Django 3.1.1 on 2021-05-24 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Suburb',
            fields=[
                ('suburb_code', models.IntegerField(primary_key=True, serialize=False)),
                ('suburb_name', models.CharField(max_length=30)),
                ('train_station', models.IntegerField()),
                ('bus_station', models.IntegerField()),
                ('hospitals', models.IntegerField()),
                ('schools', models.IntegerField()),
                ('restaurants', models.IntegerField()),
                ('shopping_center', models.IntegerField()),
                ('park', models.IntegerField()),
                ('sub_lat', models.FloatField()),
                ('sub_long', models.FloatField()),
            ],
        ),
    ]
