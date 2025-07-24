from django.contrib import admin
from .models import *

# Dynamically register all models in this app
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

app = apps.get_app_config('accounts')
for model_name, model in app.models.items():
    # Skip ChatSession so we can register it with a custom admin below
    if model.__name__ == 'ChatSession':
        continue
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass

from .models import ChatSession

# Unregister ChatSession if already registered (to avoid AlreadyRegistered error)
try:
    admin.site.unregister(ChatSession)
except admin.sites.NotRegistered:
    pass

class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_name', 'model', 'updated_at')
    search_fields = ('user__username', 'session_name', 'model')
    list_filter = ('model', 'user')
    ordering = ('-updated_at',)

admin.site.register(ChatSession, ChatSessionAdmin) 