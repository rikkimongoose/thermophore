from django.contrib import admin

from .models import Contest, Story, Vote

# Register your models here.
[admin.site.register(cls) for cls in [Contest, Story, Vote]]