from django.contrib import admin

from .models import UserProfile, UserPersona

admin.site.register(UserProfile)
admin.site.register(UserPersona)
