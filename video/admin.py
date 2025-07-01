from django.contrib import admin
from .models import Video


class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'view_count', 'create_time')
    search_fields = ('title',)
    list_filter = ('create_time',)


admin.site.register(Video, VideoAdmin)
