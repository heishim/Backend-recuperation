from django.contrib import admin

from . models import Fichier
from .models import Name, Finess

# Register your models here.

admin.site.register(Fichier)
admin.site.register(Name)
admin.site.register(Finess)
