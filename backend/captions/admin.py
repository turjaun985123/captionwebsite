from django.contrib import admin
from django.utils.html import format_html
from .models import Caption

admin.site.site_header = "কথার ঘর · কন্টেন্ট স্টুডিও"
admin.site.site_title = "কথার ঘর অ্যাডমিন"
admin.site.index_title = "আপনার ক্যাপশন পরিচালনা করুন"
admin.site.site_url = "/"
admin.site.index_template = "admin/index.html"


@admin.register(Caption)
class CaptionAdmin(admin.ModelAdmin):
    list_display = ("preview", "category", "likes", "featured_badge", "published_badge", "created_at")
    list_filter = ("category", "is_featured", "is_published", "created_at")
    search_fields = ("text", "author", "category")
    readonly_fields = ("likes", "created_at", "updated_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 25
    fieldsets = (
        ("ক্যাপশনের কথা", {"fields": ("text", "category", "author")}),
        ("প্রকাশনা ও বাছাই", {"fields": ("is_published", "is_featured")}),
        ("পাঠকের প্রতিক্রিয়া", {"fields": ("likes",)}),
        ("সময়", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    actions = ("publish_selected", "unpublish_selected", "feature_selected", "unfeature_selected")

    def changelist_view(self, request, extra_context=None):
        extra_context = {**(extra_context or {})}
        extra_context["title"] = "Your captions" if request.LANGUAGE_CODE == "en" else "আপনার ক্যাপশনসমূহ"
        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = {**(extra_context or {})}
        if request.LANGUAGE_CODE == "en":
            extra_context["title"] = "Add caption"
        else:
            extra_context["title"] = "ক্যাপশন যোগ করুন"
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = {**(extra_context or {})}
        if request.LANGUAGE_CODE == "en":
            extra_context["title"] = "Edit caption"
        else:
            extra_context["title"] = "ক্যাপশন সম্পাদনা করুন"
        return super().change_view(request, object_id, form_url, extra_context)

    def get_fieldsets(self, request, obj=None):
        if request.LANGUAGE_CODE == "en":
            return (
                ("Caption content", {"fields": ("text", "category", "author")}),
                ("Publishing and feature", {"fields": ("is_published", "is_featured")}),
                ("Reader response", {"fields": ("likes_readonly_en",)}),
                ("Timestamps", {"fields": ("created_readonly_en", "updated_readonly_en"), "classes": ("collapse",)}),
            )
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if request.LANGUAGE_CODE == "en":
            return ("likes_readonly_en", "created_readonly_en", "updated_readonly_en")
        return super().get_readonly_fields(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if request.LANGUAGE_CODE == "en":
            labels = {
                "text": "Caption", "category": "Category", "author": "Author name",
                "is_published": "Published", "is_featured": "Featured pick",
                "likes": "Likes", "created_at": "Created at", "updated_at": "Last edited",
            }
            for field, label in labels.items():
                if field in form.base_fields:
                    form.base_fields[field].label = label
        return form

    def get_list_display(self, request):
        if request.LANGUAGE_CODE == "en":
            return ("preview_en", "category_en", "likes_en", "featured_en", "published_en", "created_en")
        return super().get_list_display(request)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.LANGUAGE_CODE == "en":
            labels = {
                "publish_selected": "Publish selected captions",
                "unpublish_selected": "Move selected captions to drafts",
                "feature_selected": "Feature selected captions",
                "unfeature_selected": "Remove selected captions from featured",
            }
            for name, (_, _, _) in actions.items():
                if name in labels:
                    actions[name] = (*actions[name][:2], labels[name])
        return actions

    @admin.display(description="ক্যাপশন")
    def preview(self, obj):
        return obj.text[:75]

    @admin.display(description="বিষয়")
    def category(self, obj):
        return obj.category

    @admin.display(description="লাইক")
    def likes(self, obj):
        return obj.likes

    @admin.display(description="বিশেষ বাছাই", ordering="is_featured")
    def featured_badge(self, obj):
        label = "বিশেষ" if obj.is_featured else "সাধারণ"
        state = "is-featured" if obj.is_featured else "is-normal"
        return format_html('<span class="admin-state {}">{}</span>', state, label)

    @admin.display(description="প্রকাশিত", ordering="is_published")
    def published_badge(self, obj):
        label = "প্রকাশিত" if obj.is_published else "খসড়া"
        state = "is-live" if obj.is_published else "is-draft"
        return format_html('<span class="admin-state {}">{}</span>', state, label)

    @admin.display(description="তৈরির সময়", ordering="created_at")
    def created_at(self, obj):
        return obj.created_at

    @admin.display(description="Likes")
    def likes_readonly_en(self, obj):
        return obj.likes

    @admin.display(description="Created at")
    def created_readonly_en(self, obj):
        return obj.created_at

    @admin.display(description="Last edited")
    def updated_readonly_en(self, obj):
        return obj.updated_at

    @admin.display(description="Caption")
    def preview_en(self, obj):
        return obj.text[:75]

    @admin.display(description="Category")
    def category_en(self, obj):
        return obj.category

    @admin.display(description="Likes", ordering="likes")
    def likes_en(self, obj):
        return obj.likes

    @admin.display(description="Featured", ordering="is_featured")
    def featured_en(self, obj):
        label = "Featured" if obj.is_featured else "Standard"
        state = "is-featured" if obj.is_featured else "is-normal"
        return format_html('<span class="admin-state {}">{}</span>', state, label)

    @admin.display(description="Published", ordering="is_published")
    def published_en(self, obj):
        label = "Published" if obj.is_published else "Draft"
        state = "is-live" if obj.is_published else "is-draft"
        return format_html('<span class="admin-state {}">{}</span>', state, label)

    @admin.display(description="Created", ordering="created_at")
    def created_en(self, obj):
        return obj.created_at

    @admin.action(description="নির্বাচিত ক্যাপশন প্রকাশ করুন")
    def publish_selected(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"{count}টি ক্যাপশন প্রকাশিত হয়েছে।")

    @admin.action(description="নির্বাচিত ক্যাপশন খসড়া করুন")
    def unpublish_selected(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"{count}টি ক্যাপশন খসড়া করা হয়েছে।")

    @admin.action(description="নির্বাচিত ক্যাপশন বিশেষ বাছাই করুন")
    def feature_selected(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f"{count}টি ক্যাপশন বিশেষ বাছাইয়ে যোগ হয়েছে।")

    @admin.action(description="বিশেষ বাছাই থেকে সরান")
    def unfeature_selected(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f"{count}টি ক্যাপশন বিশেষ বাছাই থেকে সরানো হয়েছে।")
