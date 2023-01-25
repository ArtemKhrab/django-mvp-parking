# Generated by Django 4.1.5 on 2023-01-25 18:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0004_auto_20210619_1141'),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('booked', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='place',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='classroom.place'),
        ),
    ]
