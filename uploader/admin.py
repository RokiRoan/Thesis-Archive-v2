# uploader/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import Document, Tag

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'upload_date', 'view_file_link')
    search_fields = ('title', 'summary', 'extracted_text')
    list_filter = ('tags', 'upload_date')

    @admin.display(description='File Link')
    def view_file_link(self, obj):
        if obj.uploaded_file:
            return format_html('<a href="{}" target="_blank">View File</a>', obj.uploaded_file.url)
        return "No file"

# Register your models here.
admin.site.register(Document, DocumentAdmin)
admin.site.register(Tag)