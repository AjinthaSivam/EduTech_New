# Generated by Django 5.0.6 on 2024-07-08 04:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("learner", "0004_alter_learner_address_alter_learner_lastname_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="learner",
            name="firstname",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="learner",
            name="grade",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
