from rest_framework import serializers
from .models import Job, Application, Guide


class JobSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Job
        fields = (
            'id', 'title', 'category', 'company', 'organization',
            'organization_name', 'location', 'source',
            'description', 'full_description',
            'responsibilities', 'qualifications',
            'job_type', 'education_level', 'salary_range', 'deadline',
            'application_type', 'application_target', 'application_custom_text',
            'posted_date', 'expires_at', 'is_active', 'is_expired',
        )
        read_only_fields = ('posted_date', 'expires_at', 'is_expired')

    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        mapping = {
            'application_type': 'applicationType',
            'application_target': 'applicationTarget',
            'application_custom_text': 'applicationCustomText',
            'posted_date': 'postedDate',
            'expires_at': 'expiresAt',
            'organization_name': 'organizationName',
            'is_active': 'isActive',
            'is_expired': 'isExpired',
            'full_description': 'fullDescription',
            'job_type': 'jobType',
            'education_level': 'educationLevel',
            'salary_range': 'salaryRange',
        }
        for snake, camel in mapping.items():
            if snake in data:
                data[camel] = data.pop(snake)
        return data


class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = Application
        fields = (
            'id', 'job', 'job_title', 'name', 'email',
            'phone', 'cover_letter', 'cv_file', 'submitted_at',
        )
        read_only_fields = ('submitted_at',)


class GuideListSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Guide
        fields = (
            'id', 'title', 'slug', 'category', 'excerpt',
            'cover_image_url', 'author', 'read_minutes', 'published_at',
        )

    def get_cover_image_url(self, obj):
        if not obj.cover_image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.cover_image.url)
        return obj.cover_image.url


class GuideDetailSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    content_html = serializers.SerializerMethodField()

    class Meta:
        model = Guide
        fields = (
            'id', 'title', 'slug', 'category', 'excerpt',
            'content', 'content_html',
            'cover_image_url', 'author', 'read_minutes',
            'published_at', 'updated_at',
        )

    def get_cover_image_url(self, obj):
        if not obj.cover_image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.cover_image.url)
        return obj.cover_image.url

    def get_content_html(self, obj):
        import html
        blocks = [b.strip() for b in obj.content.split('\n\n') if b.strip()]
        parts = []
        for block in blocks:
            if block.startswith('### '):
                parts.append(f'<h3>{html.escape(block[4:].strip())}</h3>')
            elif block.startswith('## '):
                parts.append(f'<h2>{html.escape(block[3:].strip())}</h2>')
            elif block.startswith('# '):
                parts.append(f'<h2>{html.escape(block[2:].strip())}</h2>')
            else:
                parts.append(f'<p>{html.escape(block)}</p>')
        return ''.join(parts)