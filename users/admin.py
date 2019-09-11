from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import User
from .models import Pic

admin.site.register(User)
admin.site.register(Pic)