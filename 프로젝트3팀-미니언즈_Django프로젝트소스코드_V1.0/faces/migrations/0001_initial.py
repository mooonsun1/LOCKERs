# Generated by Django 4.2.15 on 2024-08-27 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Faces",
            fields=[
                ("face_id", models.AutoField(primary_key=True, serialize=False)),
                ("face_data_1", models.BinaryField(blank=True, null=True)),
                ("face_data_2", models.BinaryField(blank=True, null=True)),
                ("face_data_3", models.BinaryField(blank=True, null=True)),
                ("face_data_4", models.BinaryField(blank=True, null=True)),
                ("face_data_5", models.BinaryField(blank=True, null=True)),
                ("face_data_6", models.BinaryField(blank=True, null=True)),
                ("face_data_7", models.BinaryField(blank=True, null=True)),
                ("face_data_8", models.BinaryField(blank=True, null=True)),
                ("face_data_9", models.BinaryField(blank=True, null=True)),
                ("face_data_10", models.BinaryField(blank=True, null=True)),
                ("face_data_11", models.BinaryField(blank=True, null=True)),
                ("face_data_12", models.BinaryField(blank=True, null=True)),
                ("face_data_13", models.BinaryField(blank=True, null=True)),
                ("face_data_14", models.BinaryField(blank=True, null=True)),
                ("face_data_15", models.BinaryField(blank=True, null=True)),
                ("face_data_16", models.BinaryField(blank=True, null=True)),
                ("face_data_17", models.BinaryField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "faces",
                "managed": True,
            },
        ),
    ]
