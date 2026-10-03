# Step 3 of 3 — enforce unique constraint on slug

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_backfill_job_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='slug',
            field=models.SlugField(blank=True, max_length=250, unique=True),
        ),
    ]