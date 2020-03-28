from django.contrib import admin

from .models import Bird

from .models import Feeding


# Register your models here
admin.site.register(Bird)

admin.site.register(Feeding)
