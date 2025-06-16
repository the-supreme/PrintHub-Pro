from django.contrib import admin
from .models import PrintOrder, ProcessedFile

admin.site.register(PrintOrder)
admin.site.register(ProcessedFile)
