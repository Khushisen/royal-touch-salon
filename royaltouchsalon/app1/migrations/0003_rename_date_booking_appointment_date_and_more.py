# Generated by Django 5.1.1 on 2024-10-30 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app1", "0002_booking"),
    ]

    operations = [
        migrations.RenameField(
            model_name="booking",
            old_name="date",
            new_name="appointment_date",
        ),
        migrations.RenameField(
            model_name="booking",
            old_name="time",
            new_name="appointment_time",
        ),
    ]
