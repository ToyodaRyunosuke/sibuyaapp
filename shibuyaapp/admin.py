from django.contrib import admin
from .models import User, Event,password_validation

admin.site.register(User)
admin.site.register(Event)
admin.site.register(Point)