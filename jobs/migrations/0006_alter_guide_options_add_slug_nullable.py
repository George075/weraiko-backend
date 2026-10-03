# Generated manually — step 1 of 3 (add slug as nullable, apply other field changes)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0005_remove_guide_cover_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='guide',
            options={'ordering': ['-published_at']},
        ),
        migrations.AddField(
            model_name='job',
            name='slug',
            field=models.SlugField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='guide',
            name='content',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='job',
            name='category',
            field=models.CharField(
                choices=[
                    ('Technology & IT', 'Technology & IT'),
                    ('Engineering', 'Engineering'),
                    ('Customer Service', 'Customer Service'),
                    ('Business & Administration', 'Business & Administration'),
                    ('Hospitality & Tourism', 'Hospitality & Tourism'),
                    ('Health & Medicine', 'Health & Medicine'),
                    ('Education & Teaching', 'Education & Teaching'),
                    ('Sales & Marketing', 'Sales & Marketing'),
                    ('Transport & Logistics', 'Transport & Logistics'),
                    ('Security & Safety', 'Security & Safety'),
                ],
                max_length=60,
            ),
        ),
    ]