from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
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
    """Convert plain text with ## headings into safe HTML.
    Skips 'Key Responsibilities' and 'Qualifications' headings since
    those are rendered separately from the JSON fields.
    """
    if not text:
        return ''
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    blocks = [b.strip() for b in text.split('\n\n') if b.strip()]

    # Headings to skip (already rendered from JSON lists)
    SKIP_HEADINGS = {
        'key responsibilities', 'responsibilities',
        'qualifications', 'qualification and competencies',
        'qualifications and experience',
        'required experience',
    }

    parts = []
    skip_until_next_h2 = False

    for block in blocks:
        # Check if this block is an h2/h3 heading
        is_h2 = block.startswith('## ')
        is_h3 = block.startswith('### ')

        if is_h2:
            heading_text = block[3:].strip().lower()
            # If this h2 is one we render separately, skip its content
            if heading_text in SKIP_HEADINGS:
                skip_until_next_h2 = True
                continue
            else:
                skip_until_next_h2 = False
                parts.append(f'<h2>{html_module.escape(block[3:].strip())}</h2>')
                continue

        if skip_until_next_h2:
            # Inside a skipped section — don't render
            continue

        if is_h3:
            parts.append(f'<h3>{html_module.escape(block[4:].strip())}</h3>')
        elif block.startswith('# '):
            parts.append(f'<h2>{html_module.escape(block[2:].strip())}</h2>')
        else:
            parts.append(f'<p>{html_module.escape(block)}</p>')

    return ''.join(parts)return ''.join(parts)

def job_page(request, slug):
    """Server-rendered job detail page — fully crawlable by Google / AI."""
    job = get_object_or_404(Job, slug=slug)
    return render(request, 'jobs/job_page.html', {
        'job': job,
        'full_description_html': _render_full_description(job.full_description),
    })    