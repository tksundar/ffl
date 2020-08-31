from django.contrib import admin

from .forms import FileUploadForm
from .models import File_uploads, Event, Event_Admin

admin.site.site_header = 'Friends for life Events Portal admin'
admin.site.site_title = 'Events Portal admin'
# admin.site.site_url = 'http://localhost/'
admin.site.index_title = 'Events administration'
admin.empty_value_display = '**Empty**'

admin.site.register(Event)
admin.site.register(Event_Admin)
