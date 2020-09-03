from django.contrib import admin

from .models import Event, Event_Admin

admin.site.site_header = 'Events Portal admin'
admin.site.site_title = 'Events Portal admin'
#admin.site.site_url = ''
admin.site.index_title = 'Events administration'
admin.empty_value_display = '**Empty**'

admin.site.register(Event)
admin.site.register(Event_Admin)

