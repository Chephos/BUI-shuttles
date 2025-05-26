from django.contrib import admin

# Register your models here.

from bui_shuttles.trips.models import Route

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("name", "stops", "created", "modified")
    list_editable = ("stops",)