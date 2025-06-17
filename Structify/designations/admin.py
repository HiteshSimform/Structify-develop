from django.contrib import admin
from .models import Designation

# Register your models here.
# admin.site.register(Designation)
from .models import Designation

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_deleted", "created_at"]
    list_filter = ["is_deleted"]
    search_fields = ["name"]