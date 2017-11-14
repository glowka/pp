from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models.auth import User

admin.site.register(User, UserAdmin)
print ('admin')