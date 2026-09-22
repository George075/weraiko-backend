from django.contrib import admin
from .models import Job, Application, Guide


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'company', 'category', 'job_type',
        'education_level', 'location',
        'posted_date', 'expires_at', 'is_active'
    )
    list_filter = (
        'category', 'job_type', 'education_level',
        'application_type', 'is_active', 'organization'
    )
    search_fields = ('title', 'company', 'location')
    date_hierarchy = 'posted_date'
    readonly_fields = ('posted_date', 'expires_at')
    fieldsets = (
        ('Core', {
            'fields': (
                'title', 'category', 'company', 'organization',
                'location', 'source',
            )
        }),
        ('Summary', {
            'fields': ('description',),
            'description': 'Short 1–2 line summary shown on the jobs list page.'
        }),
        ('Full description', {
            'fields': ('full_description',),
            'description': (
                'The full job text shown on the detail page. '
                'Use ## for headings. Separate paragraphs with blank lines.'
            )
        }),
        ('Lists', {
            'fields': ('responsibilities', 'qualifications'),
            'description': 'JSON arrays. Example: ["Item 1", "Item 2"]'
        }),
        ('Metadata', {
            'fields': ('job_type', 'education_level', 'salary_range', 'deadline')
        }),
        ('Application', {
            'fields': ('application_type', 'application_target', 'application_custom_text')
        }),
        ('Lifecycle', {
            'fields': ('is_active', 'posted_date', 'expires_at', 'posted_by_email')
        }),
    )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'job', 'submitted_at')
    list_filter = ('submitted_at', 'job')
    search_fields = ('name', 'email', 'job__title')
    readonly_fields = ('submitted_at',)


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'read_minutes', 'is_published', 'published_at')
    list_filter = ('category', 'is_published', 'author')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('published_at', 'updated_at')
    fieldsets = (
        ('Basics', {
            'fields': ('title', 'slug', 'category', 'author', 'read_minutes', 'is_published')
        }),
        ('Content', {
            'fields': ('excerpt', 'content')
        }),
        ('Timestamps', {
            'fields': ('published_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )