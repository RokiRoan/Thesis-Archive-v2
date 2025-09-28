# uploader/models.py

from django.db import models

class Tag(models.Model):
    """A model for a single tag or category."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Document(models.Model):
    """A model for an uploaded document."""
    title = models.CharField(max_length=255, blank=True)
    uploaded_file = models.FileField(upload_to='documents/')
    extracted_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title or f"Document {self.id}"