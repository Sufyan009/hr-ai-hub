from django.contrib import admin
from .models import *

# Dynamically register all models in this app
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered

app = apps.get_app_config('accounts')
for model_name, model in app.models.items():
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass 