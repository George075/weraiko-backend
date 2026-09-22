from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone

from accounts.models import Organization


def default_expiry():
    days = getattr(settings, 'JOB_EXPIRATION_DAYS', 21)
    return timezone.now() + timedelta(days=days)


class Job(models.Model):
    """A job listing. Auto-expires after JOB_EXPIRATION_DAYS days."""

    # ---- Application method ----
    TYPE_STANDARD = 'STANDARD'
    TYPE_CV_ONLY = 'CV_ONLY'
    TYPE_LINK = 'LINK'
    TYPE_EMAIL = 'EMAIL'
    TYPE_CUSTOM = 'CUSTOM'
    TYPE_CHOICES = [
        (TYPE_CUSTOM, 'Custom method (free text)'),
        (TYPE_LINK, 'External link'),
        (TYPE_EMAIL, 'Email application'),
        (TYPE_STANDARD, 'In-app: CV + Cover Letter'),
        (TYPE_CV_ONLY, 'In-app: CV or Cover Letter'),
    ]

    # ---- Job type ----
    JT_FULL_TIME = 'FULL_TIME'
    JT_PART_TIME = 'PART_TIME'
    JT_CONTRACT = 'CONTRACT'
    JT_INTERNSHIP = 'INTERNSHIP'
    JT_REMOTE = 'REMOTE'
    JOB_TYPE_CHOICES = [
        (JT_FULL_TIME, 'Full Time'),
        (JT_PART_TIME, 'Part Time'),
        (JT_CONTRACT, 'Contract'),
        (JT_INTERNSHIP, 'Internship'),
        (JT_REMOTE, 'Remote'),
    ]

    # ---- Education level ----
    ED_CERT = 'CERTIFICATE'
    ED_DIP = 'DIPLOMA'
    ED_BACH = 'BACHELOR'
    ED_MAST = 'MASTERS'
    ED_PHD = 'PHD'
    EDUCATION_CHOICES = [
        (ED_CERT, 'Certificate'),
        (ED_DIP, 'Diploma'),
        (ED_BACH, "Bachelor's Degree"),
        (ED_MAST, "Master's Degree"),
        (ED_PHD, 'PhD'),
    ]

    # ---- Category (used by filters + frontend) ----
    CATEGORY_CHOICES = [
        ('Tech & Engineering', 'Tech & Engineering'),
        ('Business & Administration', 'Business & Administration'),
        ('Hospitality & Tourism', 'Hospitality & Tourism'),
        ('Health & Medicine', 'Health & Medicine'),
        ('Education & Teaching', 'Education & Teaching'),
        ('Sales & Marketing', 'Sales & Marketing'),
        ('Transport & Logistics', 'Transport & Logistics'),
        ('Security & Safety', 'Security & Safety'),
    ]

    # ---- Core ----
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=60, choices=CATEGORY_CHOICES)
    company = models.CharField(max_length=200, help_text='Display name shown on the card.')
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,
        null=True, blank=True, related_name='jobs',
        help_text='Leave blank for Weraiko Direct / global posts.'
    )
    location = models.CharField(max_length=120, default='Nairobi, Kenya')
    source = models.CharField(
        max_length=120, default='Direct Listing',
        help_text='e.g. Daily Nation, Gazette, Company Portal'
    )

    # ---- Detail content ----
    description = models.TextField(
        blank=True,
        help_text='Short 1-2 sentence summary shown on the list page.'
    )
    full_description = models.TextField(
        blank=True,
        help_text=(
            'Full job description as written by the employer. '
            'Use ## for headings, blank lines to separate paragraphs. '
            'This is the long-form content shown on the detail page.'
        )
    )
    responsibilities = models.JSONField(
        default=list, blank=True,
        help_text='List of strings — JSON array.'
    )
    qualifications = models.JSONField(
        default=list, blank=True,
        help_text='List of strings — JSON array.'
    )

    # ---- Metadata (new fields) ----
    job_type = models.CharField(
        max_length=20, choices=JOB_TYPE_CHOICES,
        default=JT_FULL_TIME,
        help_text='Full Time, Part Time, Contract, Internship, or Remote.'
    )
    education_level = models.CharField(
        max_length=20, choices=EDUCATION_CHOICES,
        blank=True,
        help_text='Minimum education required, if specified.'
    )
    salary_range = models.CharField(
        max_length=120, blank=True,
        help_text='e.g. Ksh 50,000 – 80,000. Leave blank if not disclosed.'
    )
    deadline = models.DateField(
        null=True, blank=True,
        help_text='Application closing date, if specified.'
    )

    # ---- Application ----
    application_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=TYPE_CUSTOM
    )
    application_target = models.CharField(
        max_length=300, blank=True,
        help_text='URL or email — only used for LINK / EMAIL types.'
    )
    application_custom_text = models.TextField(
        blank=True,
        help_text='Free-text method of application. URLs and emails auto-linkify.'
    )

    # ---- Lifecycle ----
    posted_date = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)
    is_active = models.BooleanField(default=True)
    posted_by_email = models.EmailField(blank=True)

    class Meta:
        ordering = ['-posted_date']
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'

    def __str__(self):
        return f'{self.title} @ {self.company}'

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at


class Application(models.Model):
    """A CV / cover letter submitted by an applicant."""
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    cover_letter = models.TextField(blank=True)
    cv_file = models.FileField(upload_to='applications/cvs/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'

    def __str__(self):
        return f'{self.name} → {self.job.title}'


class Guide(models.Model):
    CATEGORY_CHOICES = [
        ('CV & Resume', 'CV & Resume'),
        ('Interviews', 'Interviews'),
        ('Salary', 'Salary'),
        ('Career Growth', 'Career Growth'),
        ('Job Search', 'Job Search'),
        ('Workplace', 'Workplace'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=60, choices=CATEGORY_CHOICES)
    excerpt = models.CharField(max_length=320)
    content = models.TextField()
    author = models.CharField(max_length=120, default='Weraiko Team')
    read_minutes = models.PositiveIntegerField(default=4)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base = slugify(self.title)
            slug = base
            n = 1
            while Guide.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f'{base}-{n}'
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} ({self.category})'