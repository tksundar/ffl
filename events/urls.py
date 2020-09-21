import os

from django.conf import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [path("", views.login, name='login'), ]
urlpatterns += [path("newuser", views.new_user, name='new_user'), ]
urlpatterns += [path("change_password", views.change_password, name='change_password'), ]
urlpatterns += [path("<int:event_id>/index", views.index, name='index'), ]
urlpatterns += [path("logout", views.logout, name='logout'), ]
urlpatterns += [path("list_events", views.list_events, name='list_events'), ]
urlpatterns += [path("detail", views.detail, name='detail'), ]
urlpatterns += [path("<int:event_id>/registrations", views.registrations, name='registrations'), ]
urlpatterns += [path("<int:event_id>/deleted_view", views.deleted_view, name='deleted_view'), ]
urlpatterns += [path("<int:event_id>/register", views.register, name='register'), ]
urlpatterns += [path("<int:event_id>/register-again", views.register_again, name='register_again'), ]
urlpatterns += [path("<int:reg_id>/edit", views.edit, name='edit'), ]
urlpatterns += [path("<int:reg_id>/delete", views.delete, name='delete'), ]
urlpatterns += [path("<int:event_id>/stats", views.stats, name='stats'), ]
urlpatterns += [path('password_reset', views.password_reset, name='password_reset'), ]
urlpatterns += [path("<int:event_id>/upload", views.upload, name='upload'), ]
urlpatterns += [path("<int:event_id>/display_media", views.display_media, name='display_media'), ]
urlpatterns += [path("<int:event_id>/delete", views.delete_media, name='delete_media'), ]
urlpatterns += [path("<int:image_id>/show_media", views.show_media, name='show_media'), ]
urlpatterns += [path("<int:csv_id>/export/csv", views.export_csv, name='export_csv'), ]

if os.getenv('DEBUG') == 'True':
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
