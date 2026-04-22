from .models import Profile
from django.contrib import admin
from .models import Incident, AnonymousReport

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_occurred', 'status', 'created_by')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description')
    actions = ['confirm_incidents']
    def confirm_incidents(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f"{queryset.count()} происшествий подтверждено.")
    confirm_incidents.short_description = "Подтвердить выбранные происшествия"

@admin.register(AnonymousReport)
class AnonymousReportAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at', 'location')
    readonly_fields = ('subject', 'message', 'location', 'created_at')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__username',)
