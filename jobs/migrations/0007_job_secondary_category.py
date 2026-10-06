from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_alter_guide_options_add_slug_nullable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='category',
            field=models.CharField(
                choices=[
                    ('Technology & IT', 'Technology & IT'),
                    ('Engineering', 'Engineering'),
                    ('Customer Service', 'Customer Service'),
                    ('Business & Administration', 'Business & Administration'),
                    ('Human Resources (HR)', 'Human Resources (HR)'),
                    ('Finance & Accounting', 'Finance & Accounting'),
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
        migrations.AddField(
            model_name='job',
            name='secondary_category',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Technology & IT', 'Technology & IT'),
                    ('Engineering', 'Engineering'),
                    ('Customer Service', 'Customer Service'),
                    ('Business & Administration', 'Business & Administration'),
                    ('Human Resources (HR)', 'Human Resources (HR)'),
                    ('Finance & Accounting', 'Finance & Accounting'),
                    ('Hospitality & Tourism', 'Hospitality & Tourism'),
                    ('Health & Medicine', 'Health & Medicine'),
                    ('Education & Teaching', 'Education & Teaching'),
                    ('Sales & Marketing', 'Sales & Marketing'),
                    ('Transport & Logistics', 'Transport & Logistics'),
                    ('Security & Safety', 'Security & Safety'),
                ],
                help_text='Optional. Makes the job appear in a second category listing too.',
                max_length=60,
                null=True,
            ),
        ),
    ]
