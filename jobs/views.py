from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.db.models import Q
from django.utils.text import slugify
import html as html_module
import re

from .models import Job, Application, Guide
from .serializers import (
    JobSerializer, ApplicationSerializer,
    GuideListSerializer, GuideDetailSerializer,
)


# ============================================================
# Public API
# ============================================================

def active_jobs_qs():
    """All jobs that should be publicly visible right now."""
    return (
        Job.objects
        .filter(is_active=True, expires_at__gt=timezone.now())
        .order_by('-posted_date')
    )


@api_view(['GET'])
def job_list(request):
    """GET /api/jobs/ — public list of active jobs."""
    jobs = active_jobs_qs()
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def job_detail(request, pk):
    """GET /api/jobs/<id>/ — public single job."""
    try:
        job = active_jobs_qs().get(pk=pk)
    except Job.DoesNotExist:
        return Response({'detail': 'Job not found or expired.'},
                        status=status.HTTP_404_NOT_FOUND)
    return Response(JobSerializer(job).data)


@api_view(['POST'])
def job_apply(request, pk):
    """POST /api/jobs/<id>/apply/ — submit an application."""
    try:
        job = active_jobs_qs().get(pk=pk)
    except Job.DoesNotExist:
        return Response({'detail': 'Job not found or expired.'},
                        status=status.HTTP_404_NOT_FOUND)

    serializer = ApplicationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(job=job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def guide_list(request):
    """GET /api/guides/ — public list of published guides."""
    guides = Guide.objects.filter(is_published=True).order_by('-published_at')
    serializer = GuideListSerializer(guides, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def guide_detail(request, slug):
    """GET /api/guides/<slug>/ — full guide."""
    try:
        guide = Guide.objects.get(slug=slug, is_published=True)
    except Guide.DoesNotExist:
        return Response({'detail': 'Guide not found.'},
                        status=status.HTTP_404_NOT_FOUND)
    serializer = GuideDetailSerializer(guide, context={'request': request})
    return Response(serializer.data)


# ============================================================
# Helpers — full description + custom text link extraction
# ============================================================

def _render_full_description(text):
    """Convert plain text with ## headings into safe HTML."""
    if not text:
        return ''
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    blocks = [b.strip() for b in text.split('\n\n') if b.strip()]
    parts = []
    for block in blocks:
        if block.startswith('### '):
            parts.append(f'<h3>{html_module.escape(block[4:].strip())}</h3>')
        elif block.startswith('## '):
            parts.append(f'<h2>{html_module.escape(block[3:].strip())}</h2>')
        elif block.startswith('# '):
            parts.append(f'<h2>{html_module.escape(block[2:].strip())}</h2>')
        else:
            parts.append(f'<p>{html_module.escape(block)}</p>')
    return ''.join(parts)


def _extract_link(text):
    """Extract the first email or URL from custom text.
    Returns (kind, value) where kind is 'email' | 'link' | None."""
    if not text:
        return (None, None)

    email_match = re.search(
        r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b',
        text,
    )
    if email_match:
        return ('email', email_match.group(1))

    url_match = re.search(
        r'((?:https?://|www\.)[^\s<>"\']+)',
        text,
    )
    if url_match:
        url = url_match.group(1).rstrip('.,;:)!?')
        if not url.startswith('http'):
            url = 'https://' + url
        return ('link', url)

    return (None, None)


# ============================================================
# Server-rendered job detail page (SSR)
# ============================================================

def job_page(request, slug):
    """Server-rendered job detail page — fully crawlable by Google / AI."""
    job = get_object_or_404(Job, slug=slug)

    related = (
        Job.objects
        .filter(is_active=True, category=job.category)
        .exclude(pk=job.pk)
        .order_by('-posted_date')[:3]
    )

    # If application_type is CUSTOM but there is a URL or email in the
    # custom text, extract it so the template can render an apply button.
    auto_kind, auto_target = (None, None)
    if job.application_type == 'CUSTOM' and job.application_custom_text:
        auto_kind, auto_target = _extract_link(job.application_custom_text)

    return render(request, 'jobs/job_page.html', {
        'job': job,
        'full_description_html': _render_full_description(job.full_description),
        'related_jobs': related,
        'auto_apply_kind': auto_kind,
        'auto_apply_target': auto_target,
    })


# ============================================================
# SEO Landing Pages — Education + Category
# ============================================================

EDUCATION_SLUGS = {
    'certificate-jobs-in-kenya':  ('CERTIFICATE', 'Certificate Jobs in Kenya'),
    'diploma-jobs-in-kenya':      ('DIPLOMA',     'Diploma Jobs in Kenya'),
    'degree-jobs-in-kenya':       ('BACHELOR',    'Degree Jobs in Kenya'),
    'masters-jobs-in-kenya':      ('MASTERS',     "Master's Jobs in Kenya"),
    'form-four-leavers-jobs':     ('CERTIFICATE', 'Form Four Leaver Jobs in Kenya'),
}

CATEGORY_SLUGS = {
    'ict-jobs-in-kenya':              ('Technology & IT',           'ICT & IT Jobs in Kenya'),
    'engineering-jobs-in-kenya':      ('Engineering',               'Engineering Jobs in Kenya'),
    'customer-service-jobs-in-kenya': ('Customer Service',          'Customer Service Jobs in Kenya'),
    'business-jobs-in-kenya':         ('Business & Administration', 'Business & Admin Jobs in Kenya'),
    'hr-jobs-in-kenya':               ('Human Resources (HR)',      'Human Resources (HR) Jobs in Kenya'),
    'finance-jobs-in-kenya':          ('Finance & Accounting',      'Finance & Accounting Jobs in Kenya'),
    'hospitality-jobs-in-kenya':      ('Hospitality & Tourism',     'Hospitality & Tourism Jobs in Kenya'),
    'health-jobs-in-kenya':           ('Health & Medicine',         'Health & Medical Jobs in Kenya'),
    'teaching-jobs-in-kenya':         ('Education & Teaching',      'Teaching Jobs in Kenya'),
    'sales-jobs-in-kenya':            ('Sales & Marketing',         'Sales & Marketing Jobs in Kenya'),
    'transport-jobs-in-kenya':        ('Transport & Logistics',     'Transport & Logistics Jobs in Kenya'),
    'security-jobs-in-kenya':         ('Security & Safety',         'Security & Safety Jobs in Kenya'),
}


def _seo_jobs_qs(**filters):
    """Active jobs filtered by given fields, newest first."""
    return (
        Job.objects
        .filter(is_active=True, expires_at__gt=timezone.now(), **filters)
        .order_by('-posted_date')
    )


def education_jobs(request, slug):
    """SEO landing page: /jobs/education/<slug>/."""
    if slug not in EDUCATION_SLUGS:
        raise Http404('Unknown education slug')
    level, heading = EDUCATION_SLUGS[slug]

    if level == 'CERTIFICATE':
        jobs = (
            Job.objects
            .filter(is_active=True, expires_at__gt=timezone.now())
            .filter(Q(education_level='CERTIFICATE') | Q(education_level=''))
            .order_by('-posted_date')
        )
    else:
        jobs = _seo_jobs_qs(education_level=level)

    return render(request, 'jobs/seo_landing.html', {
        'jobs': jobs,
        'heading': heading,
        'intro': (
            f'Browse {jobs.count()} verified {heading.lower()} — updated daily. '
            'No sign-up required. Free to apply.'
        ),
        'canonical_url': f'https://wera-iko.co.ke/jobs/education/{slug}/',
        'page_kind': 'education',
    })


def category_jobs(request, slug):
    """SEO landing page: /jobs/category/<slug>/."""
    if slug not in CATEGORY_SLUGS:
        raise Http404('Unknown category slug')
    category, heading = CATEGORY_SLUGS[slug]

    # Match jobs whose primary OR secondary category equals this category
    jobs = (
        Job.objects
        .filter(is_active=True, expires_at__gt=timezone.now())
        .filter(Q(category=category) | Q(secondary_category=category))
        .order_by('-posted_date')
    )

    return render(request, 'jobs/seo_landing.html', {
        'jobs': jobs,
        'heading': heading,
        'intro': (
            f'Browse {jobs.count()} verified {heading.lower()} — updated daily. '
            'No sign-up required. Free to apply.'
        ),
        'canonical_url': f'https://wera-iko.co.ke/jobs/category/{slug}/',
        'page_kind': 'category',
    })


# ============================================================
# Location Landing Pages
# ============================================================

LOCATION_SLUGS = {
    'nairobi-jobs':      ('Nairobi, Kenya',   'Jobs in Nairobi'),
    'mombasa-jobs':      ('Mombasa, Kenya',   'Jobs in Mombasa'),
    'kisumu-jobs':       ('Kisumu, Kenya',    'Jobs in Kisumu'),
    'nakuru-jobs':       ('Nakuru, Kenya',    'Jobs in Nakuru'),
    'eldoret-jobs':      ('Eldoret, Kenya',   'Jobs in Eldoret'),
    'thika-jobs':        ('Thika, Kenya',     'Jobs in Thika'),
    'athi-river-jobs':   ('Athi River, Kenya','Jobs in Athi River'),
    'kajiado-jobs':      ('Kajiado, Kenya',   'Jobs in Kajiado'),
    'machakos-jobs':     ('Machakos, Kenya',  'Jobs in Machakos'),
    'meru-jobs':         ('Meru, Kenya',      'Jobs in Meru'),
    'kisii-jobs':        ('Kisii, Kenya',     'Jobs in Kisii'),
    'kericho-jobs':      ('Kericho, Kenya',   'Jobs in Kericho'),
    'nyeri-jobs':        ('Nyeri, Kenya',     'Jobs in Nyeri'),
    'embu-jobs':         ('Embu, Kenya',      'Jobs in Embu'),
    'kitui-jobs':        ('Kitui, Kenya',     'Jobs in Kitui'),
}


def location_jobs(request, slug):
    """SEO landing page: /jobs/location/<slug>/ (e.g. nairobi-jobs)."""
    if slug not in LOCATION_SLUGS:
        raise Http404('Unknown location slug')
    location, heading = LOCATION_SLUGS[slug]
    jobs = _seo_jobs_qs(location=location)

    return render(request, 'jobs/seo_landing.html', {
        'jobs': jobs,
        'heading': heading,
        'intro': (
            f'Browse {jobs.count()} verified {heading.lower()} — updated daily. '
            'No sign-up required. Free to apply.'
        ),
        'canonical_url': f'https://wera-iko.co.ke/jobs/location/{slug}/',
        'page_kind': 'location',
    })


# ============================================================
# Company Landing Pages
# ============================================================

def _slugify_company(name):
    """Convert a company name to a URL-safe slug."""
    return slugify(name or '')


def company_jobs(request, slug):
    """SEO landing page: /companies/<slug>/ (e.g. /companies/kcb-group/)."""
    all_jobs = Job.objects.filter(
        is_active=True,
        expires_at__gt=timezone.now(),
    ).order_by('-posted_date')

    # Match by slugified company name
    jobs = [j for j in all_jobs if _slugify_company(j.company) == slug]

    if not jobs:
        # Try substring matches (handles "Company XYZ" vs "Company-XYZ")
        possible = [
            j for j in all_jobs
            if slug.replace('-', '') in _slugify_company(j.company).replace('-', '')
            or _slugify_company(j.company).replace('-', '') in slug.replace('-', '')
        ]
        if possible:
            jobs = possible
        else:
            raise Http404(f'No jobs found for company: {slug}')

    display_name = jobs[0].company if jobs else slug.replace('-', ' ').title()

    return render(request, 'jobs/seo_landing.html', {
        'jobs': jobs,
        'heading': f'{display_name} Jobs in Kenya',
        'intro': (
            f'Browse {len(jobs)} verified job openings at {display_name} in Kenya. '
            'Updated daily. Free to apply.'
        ),
        'canonical_url': f'https://wera-iko.co.ke/companies/{slug}/',
        'page_kind': 'company',
    })


def companies_index(request):
    """Public index of all companies with active jobs: /companies/."""
    all_jobs = Job.objects.filter(
        is_active=True,
        expires_at__gt=timezone.now(),
    ).order_by('-posted_date')

    company_counts = {}
    company_display = {}
    for job in all_jobs:
        if not job.company:
            continue
        slug = _slugify_company(job.company)
        if not slug:
            continue
        company_counts[slug] = company_counts.get(slug, 0) + 1
        company_display[slug] = job.company

    companies = [
        {
            'slug': slug,
            'name': company_display[slug],
            'count': company_counts[slug],
        }
        for slug in sorted(
            company_counts,
            key=lambda s: (-company_counts[s], company_display[s].lower()),
        )
    ]

    return render(request, 'jobs/companies_index.html', {
        'companies': companies,
        'total_companies': len(companies),
        'total_jobs': sum(company_counts.values()),
    })
