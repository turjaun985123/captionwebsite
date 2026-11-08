from django import template
from captions.models import Caption

register = template.Library()


@register.simple_tag
def caption_dashboard_data():
    return {
        "draft_count": Caption.objects.filter(is_published=False).count(),
        "drafts": Caption.objects.filter(is_published=False).order_by("-updated_at")[:5],
        "recent_captions": Caption.objects.order_by("-updated_at")[:8],
        "caption_count": Caption.objects.count(),
    }
