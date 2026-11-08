from django.db import models
from django.utils.text import slugify

class Caption(models.Model):
    text = models.TextField("ক্যাপশন", max_length=500)
    category = models.CharField("বিষয়", max_length=40, default="অনুভূতি", db_index=True)
    author = models.CharField("লেখকের নাম", max_length=80, blank=True)
    likes = models.PositiveIntegerField("লাইক", default=0)
    is_featured = models.BooleanField("বিশেষ বাছাই", default=False)
    is_published = models.BooleanField("প্রকাশিত", default=True, db_index=True)
    created_at = models.DateTimeField("তৈরির সময়", auto_now_add=True)
    updated_at = models.DateTimeField("সর্বশেষ সম্পাদনা", auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        verbose_name = "ক্যাপশন"
        verbose_name_plural = "ক্যাপশনসমূহ"

    def __str__(self):
        return self.text[:65]

    @property
    def slug(self):
        return slugify(self.text[:48]) or f"caption-{self.pk}"
