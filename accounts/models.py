from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Organization(models.Model):
    """A company / publisher that posts jobs on Weraiko."""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='org_logos/', blank=True, null=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text='Inactive organizations cannot have their jobs shown publicly.'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while Organization.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                n += 1
                slug = f'{base}-{n}'
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AdminProfile(models.Model):
    """Links a Django User to a role + (optionally) an Organization."""
    ROLE_SUPER = 'SUPER_ADMIN'
    ROLE_ORG = 'ORG_ADMIN'
    ROLE_SUB = 'SUB_ADMIN'
    ROLE_CHOICES = [
        (ROLE_SUPER, 'Super Admin'),
        (ROLE_ORG, 'Organization Admin'),
        (ROLE_SUB, 'Sub Admin'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='admin_profile'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ORG)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,
        null=True, blank=True, related_name='admins',
        help_text='Leave blank for Super Admin.'
    )
    phone = models.CharField(max_length=30, blank=True)
    must_change_password = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__username']
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'

    def __str__(self):
        org = self.organization.name if self.organization else '—'
        return f'{self.user.username} ({self.get_role_display()}) @ {org}'

    @property
    def is_super_admin(self):
        return self.role == self.ROLE_SUPER