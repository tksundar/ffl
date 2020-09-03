from django import forms

from .models import Event


class EventsDateInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class RegistrationForm(forms.Form):
    yes_no = [('Yes', 'Yes'), ('No', 'No')]
    event = forms.HiddenInput()
    first_name = forms.CharField(max_length=20, widget=forms.TextInput)
    last_name = forms.CharField(max_length=20, widget=forms.TextInput)
    email = forms.HiddenInput()
    mobile = forms.CharField(widget=forms.TextInput)
    payment_amount = forms.CharField(widget=forms.TextInput)
    payment_ref = forms.CharField(widget=forms.TextInput)
    extended_tour = forms.ChoiceField(choices=yes_no)
    num_of_guests = forms.CharField(widget=forms.TextInput)
    num_of_days = forms.CharField(widget=forms.TextInput)
    mode_of_travel = forms.ChoiceField(choices=[('Air', 'Air'), ('Train', 'Train'), ('Road', 'Road')])
    arrival_date = forms.DateTimeField(widget=EventsDateInput)
    departure_date = forms.DateTimeField(widget=EventsDateInput)
    pickup_reqd = forms.ChoiceField(choices=yes_no)
    special_req = forms.CharField(widget=forms.TextInput)


class FileUploadForm(forms.Form):
    event = forms.HiddenInput
    file_url = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))




# class FileUploadForm(forms.ModelForm):
#     class Meta:
#         model = File_uploads
#         fields = '__all__'
#         widgets = {
#             'event': forms.Select,
#             'file_url': forms.ClearableFileInput(attrs={'multiple': True}),
#         }
#         labels = {
#             'file_url': 'files'
#         }
#
#         help_texts = {
#             'file_url': ''
#         }
