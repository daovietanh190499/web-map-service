from django.contrib import admin
from .models import Topic, TopicAttachment

class TopicAttachmentInline(admin.TabularInline):
    model = TopicAttachment
    extra = 1
    fields = ['file', 'filename', 'file_size', 'file_type']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['topic_name', 'type', 'subject', 'area', 'created_date', 'created_by']
    list_filter = ['type', 'created_date', 'subject', 'area']
    search_fields = ['topic_name', 'content', 'subject', 'area']
    readonly_fields = ['id', 'created_date', 'updated_at']
    inlines = [TopicAttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('topic_name', 'type', 'subject', 'area')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_date', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TopicAttachment)
class TopicAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'topic', 'file_type', 'file_size', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['filename', 'topic__topic_name']
    readonly_fields = ['id', 'file_size', 'file_type', 'uploaded_at']
