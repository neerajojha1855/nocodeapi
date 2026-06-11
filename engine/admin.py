from django.contrib import admin
from .models import DynamicAPI, APIField, compile_virtual_model, execute_runtime_migration

class APIFieldInline(admin.TabularInline):
    model = APIField
    extra = 1

@admin.register(DynamicAPI)
class DynamicAPIAdmin(admin.ModelAdmin):
    inlines = [APIFieldInline]
    list_display = ('name', 'slug', 'active')

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        api_instance = form.instance
        RuntimeModel = compile_virtual_model(api_instance)

        execute_runtime_migration(RuntimeModel)