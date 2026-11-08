from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Caption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField(max_length=500)),
                ("category", models.CharField(db_index=True, default="Everyday", max_length=40)),
                ("author", models.CharField(blank=True, max_length=80)),
                ("likes", models.PositiveIntegerField(default=0)),
                ("is_featured", models.BooleanField(default=False)),
                ("is_published", models.BooleanField(db_index=True, default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-is_featured", "-created_at"]},
        ),
    ]
