from django.contrib import admin

from plates.models import Plate,Cond,Treatment, Well

admin.site.register(Plate)
admin.site.register(Cond)
admin.site.register(Well)
admin.site.register(Treatment)