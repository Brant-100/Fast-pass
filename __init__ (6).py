from django.contrib import admin
from .models import ThemeZone, Attraction, TimeSlot, Guest, FastPass


@admin.register(ThemeZone)
class ThemeZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_open', 'created_at']
    list_filter = ['is_open']
    search_fields = ['name', 'description']


@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ['name', 'zone', 'attraction_type', 'thrill_level',
                    'current_wait_minutes', 'is_operational']
    list_filter = ['zone', 'attraction_type', 'thrill_level', 'is_operational']
    search_fields = ['name', 'description']
    list_editable = ['current_wait_minutes', 'is_operational']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['attraction', 'start_time', 'end_time',
                    'max_fastpasses', 'is_active']
    list_filter = ['attraction__zone', 'is_active']
    ordering = ['attraction', 'start_time']


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email',
                    'membership_tier', 'daily_fastpass_limit']
    list_filter = ['membership_tier']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(FastPass)
class FastPassAdmin(admin.ModelAdmin):
    list_display = ['guest', 'attraction', 'time_slot',
                    'booking_date', 'status']
    list_filter = ['status', 'booking_date', 'attraction__zone']
    search_fields = ['guest__first_name', 'guest__last_name']
    date_hierarchy = 'booking_date'
