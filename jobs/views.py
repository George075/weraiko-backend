from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from django.http import Http404
import html as html_module

from .models import Job, Application, Guide
from .serializers import JobSerializer, ApplicationSerializer

from .models import Guide
from .serializers import GuideListSerializer, GuideDetailSerializer


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
        return Response({'detail': 'Guide not found.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = GuideDetailSerializer(guide, context={'request': request})
    return Response(serializer.data)


# ============================================================
# Server-rendered job page (for SEO + AI crawlers)
# ============================================================



def _render_full_description(text):
    """Convert plain text with ## headings into safe HTML."""
    if not text:
        return ''
    # Normalise line endings (Windows \r\n and Mac \r -> Unix \n)
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

def job_page(request, slug):
    job = get_object_or_404(Job, slug=slug)
    return render(request, 'jobs/job_page.html', {
        'job': job,
        'full_description_html': '',
        'related_jobs': [],
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
    """SEO landing page: /jobs/education/<slug>/  (e.g. diploma-jobs-in-kenya)."""
    if slug not in EDUCATION_SLUGS:
        raise Http404('Unknown education slug')
    level, heading = EDUCATION_SLUGS[slug]
    jobs = _seo_jobs_qs(education_level=level)

    # Also include empty-education jobs for certificate / form-four pages
    if level == 'CERTIFICATE':
        from django.db.models import Q
        jobs = (
            Job.objects
            .filter(is_active=True, expires_at__gt=timezone.now())
            .filter(Q(education_level='CERTIFICATE') | Q(education_level=''))
            .order_by('-posted_date')
        )

    return render(request, 'jobs/seo_landing.html', {
        'jobs': jobs,
        'heading': heading,
        'intro': (
            f'Browse {jobs.count()} verified {heading.lower()} — updated daily. '
            'No sign-up required. Free to apply.'
        ),
        'canonical_url': f'https://www.wera-iko.co.ke/jobs/education/{slug}/',
        'page_kind': 'education',
    })


def category_jobs(request, slug):
    """SEO landing page: /jobs/category/<slug>/  (e.g. ict-jobs-in-kenya)."""
    if slug not in CATEGORY_SLUGS:
        raise Http404('Unknown category slug')
    category, heading = CATEGORY_SLUGS[slug]
    jobs = _seo_jobs_qs(category=category)

    return render(request, 'jobs/seo_landing.html', {
        'jobs': jobs,
        'heading': heading,
        'intro': (
            f'Browse {jobs.count()} verified {heading.lower()} — updated daily. '
            'No sign-up required. Free to apply.'
        ),
        'canonical_url': f'https://www.wera-iko.co.ke/jobs/category/{slug}/',
        'page_kind': 'category',
    })
    return render(request, 'jobs/job_page.html', {
        'job': job,
        'full_description_html': _render_full_description(job.full_description),
        'related_jobs': related,
    })
