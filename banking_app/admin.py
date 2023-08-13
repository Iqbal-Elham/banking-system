from django.contrib import admin

from .models import UserMessage

@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('subject', 'name', 'email', 'message')
