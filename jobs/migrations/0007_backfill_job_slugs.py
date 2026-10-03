# Step 2 of 3 — backfill unique slugs for existing jobs

from django.db import migrations
from django.utils.text import slugify


def backfill_slugs(apps, schema_editor):
    Job = apps.get_model('jobs', 'Job')
    seen = set()
    for job in Job.objects.all().order_by('pk'):
        if job.slug:
            seen.add(job.slug)
            continue
        base = slugify(f'{job.title} {job.company}')[:230] or f'job-{job.pk}'
        slug = base
        n = 1
        while slug in seen or Job.objects.filter(slug=slug).exclude(pk=job.pk).exists():
            n += 1
            slug = f'{base}-{n}'
        job.slug = slug
        seen.add(slug)
        job.save(update_fields=['slug'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_alter_guide_options_add_slug_nullable'),
    ]

    operations = [
        migrations.RunPython(backfill_slugs, noop),
    ]