import copy
import csv
import logging
import random
import string
from datetime import timedelta
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .forms import RegistrationForm, FileUploadForm
from .models import Login, Event, Registration, Registration_stats, File_uploads, Event_Admin

logger = logging.getLogger('ffl.views')


def check_if_password_change(request):
    # if this is a temp password. Return change password page.Temp passwords are 5 chars long
    _pwd = request.POST['pwd']
    if len(_pwd) != 5:
        return False
    try:
        Login.objects.get(temp_password__exact=_pwd)
        return render(request, 'events/change_password.html', {'user', None})
    except Login.DoesNotExist:
        return render(request, 'events/new_user.html', {'err': 'No such user. Please register'})


def check_user_is_event_admin(user, event_id):
    try:
        if user:
            admins = Event_Admin.objects.get(Q(admin=user.username), Q(event_id=event_id))
            return admins
    except Event_Admin.DoesNotExist:
        return None


def check_login(request):
    email = request.POST['email']
    try:
        _login = Login.objects.get(email__exact=email)
        _pwd = request.POST['pwd']
        check_if_password_change(request)
        pwd = _login.password
        logger.debug('checking password')
        if not check_password(_pwd, pwd):
            ret_val = 'invalid password'
        else:
            ret_val = _login
    except Login.DoesNotExist:
        ret_val = 'Email not recognized. Please register'
    return ret_val


def login(request):
    events = Event.objects.all().order_by('event_date')
    logger.debug('retrieved events %s' % events)
    if request.POST:
        ret_val = check_login(request)
        if isinstance(ret_val, Login):
            request.session['username'] = ret_val.username
            request.session['email'] = ret_val.email
            return render(request, 'events/index.html', {'user': ret_val, 'events': events})
        else:
            err = str(ret_val)
            return render(request, 'events/login.html', {'user': None, 'err': err})
    else:
        _login = None
        user: Login = create_user(request)
        if user:
            # admin = check_user_is_event_admin(user,)
            logger.info('User %s logged in' % user.username)
            return render(request, 'events/index.html', {'events': events, 'user': user})
        else:
            return render(request, 'events/login.html', {'user': create_user(request)})


def create_new_password():
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(5))
    return result_str


def change_password(request):
    if request.POST:
        old_password = request.POST['current']
        new_password = request.POST['pwd']
        new_password_confirm = request.POST['pwd1']
        if new_password != new_password_confirm and len(new_password) < 6:
            return render(request, 'events/change_password.html', {'err': 'passwords do not match', 'user': None})
        try:
            login_ = Login.objects.get(temp_password__exact=old_password)
            logger.info('password change for user % started ' % login_.username)
            login_new = copy.deepcopy(login_)
            login_new.temp_password = ''
            login_new.password = make_password(new_password)
            login_.delete()
            login_new.save()
            return render(request, 'events/login.html', {'err': 'login with new password'})
        except Login.DoesNotExist:
            logger.error('Unknown user')
            ctx = {'err': 'User does not exist. Please register', 'user': None}
            return render(request, 'events/new_user.html', ctx)
    else:
        raise Http404("Resource not found")


def password_reset(request):
    if request.POST:
        email_id = request.POST['email']
        try:
            login_ = Login.objects.get(email__exact=email_id)
            login_new = copy.deepcopy(login_)
            login_.delete()
            pwd_temp = create_new_password()
            login_new.temp_password = pwd_temp
            login_new.save()
            return render(request, 'events/change_password.html', {'old': pwd_temp, 'user': None})
        except Login.DoesNotExist:
            ctx = {'err': 'User does not exist. Please register', 'user': None}
            return render(request, 'events/new_user.html', ctx)
    else:
        return render(request, 'events/password_reset.html', {'user': None})


def login_present(request, username, email_id):
    u1 = Login.objects.filter(username__exact=username)
    u2 = Login.objects.filter(email__exact=email_id)
    return u1.exists() or u2.exists()


def validate_new_user(request):
    email_id = str(request.POST['email']).strip()
    username = str(request.POST['username']).strip()
    pwd = str(request.POST['pwd']).strip()
    pwd1 = str(request.POST['pwd1']).strip()

    if login_present(request, username, email_id):
        return 'Either username or password is taken'

    if len(username) < 3:
        return 'Valid username with 3 or more characters required'

    if len(email_id) < 8:
        return 'Valid email with 8 or more characters required'

    if len(pwd) < 6:
        return 'password must have 6 or more characters'

    if pwd != pwd1:
        return 'password and confirm password do not match'

    return email_id, username, pwd


def new_user(request):
    if request.POST:
        val = validate_new_user(request)
        if isinstance(val, str):
            logger.error('error creating new user <%s>' % str(val))
            return render(request, 'events/new_user.html', {'err': val, 'user': None})
        email_id, username, pwd = val
        _login = Login()
        _login.email = email_id
        _login.password = make_password(pwd)
        _login.username = username
        _login.save()
        logger.debug('New User %s registered ' % _login.username)
        request.session['email'] = _login.email
        request.session['username'] = _login.username
        return render(request, 'events/confirm.html', {'user': _login})
    else:
        return render(request, 'events/new_user.html', {'err': '', 'user': None})


def list_events(request):
    events = Event.objects.all().order_by('event_date')
    user = create_user(request)
    if user:
        return render(request, 'events/index.html',
                      {'events': events, 'user': user})
    else:
        return render(request, 'events/login.html', {'err': 'Session expired. Please login again'})


def index(request, event_id):
    event = Event.objects.get(id=event_id)
    user = create_user(request)
    admin = check_user_is_event_admin(user, event_id)
    if user:
        return render(request, 'events/event_detail.html',
                      {'event': event, 'user': user, 'admin': admin, 'now': timezone.now()})
    else:
        return render(request, 'events/login.html', {'err': 'Session expired. Please login again'})


def set_initial(reg_form, event, email):
    reg_form.initial = {
        'event': event.event_name,
        'num_of_guests': '1',
        'num_of_days': '2',
        'email': email,
        'special_req': 'None'
    }


def create_registration(form, event, email):
    registration = Registration()
    registration.event = event
    registration.first_name = form.cleaned_data['first_name']
    registration.last_name = form.cleaned_data['last_name']
    registration.num_days = form.cleaned_data['num_of_days']
    registration.num_guests = form.cleaned_data['num_of_guests']
    registration.mobile = form.cleaned_data['mobile']
    registration.email = email
    registration.payment_amount = form.cleaned_data['payment_amount']
    registration.payment_ref = form.cleaned_data['payment_ref']
    registration.extended_tour = form.cleaned_data['extended_tour']
    registration.mode_of_travel = form.cleaned_data['mode_of_travel']
    registration.pickup_reqd = form.cleaned_data['pickup_reqd']
    registration.arrival_date = form.cleaned_data['arrival_date']
    registration.departure_date = form.cleaned_data['departure_date']
    registration.special_req = form.cleaned_data['special_req']
    return registration


def delete_if_present(request, email_id):
    try:
        reg = Registration.objects.get(email__exact=email_id)
        # we got one. Lets delete.
        reg.delete()
    except Registration.DoesNotExist:
        # do nothing
        pass


def registration_is_valid(reg: Registration, event: Event):
    arr_date = reg.arrival_date.date()
    dep_date = reg.departure_date.date()
    event_date = event.event_date.date()

    if arr_date <= dep_date and \
            arr_date <= event_date and \
            int(reg.num_days) > 0 and \
            int(reg.num_guests) > 0:
        return True
    return False


def populate_stats(user, event):
    try:
        Registration_stats.objects.get(username__exact=user.username)
        return HttpResponse('Somebody with the same username has already registered.This is very unusual!')
    except Registration_stats.DoesNotExist:
        stats_ = Registration_stats()
        stats_.event = event
        stats_.username = user.username
        stats_.save()


def check_deletable(event_date):
    event_date_without_time = event_date.date()
    now = timezone.now().date()
    return (event_date_without_time - now) > timedelta(days=7)


def register(request, event_id):
    event: Event = Event.objects.get(pk=event_id)
    logger.debug('registering for event %s' % event.event_name)
    user: Login = create_user(request)
    if not user:
        logger.debug('request method is %s' % request.method)
        return render(request, 'events/new_user.html', {'err': "User not registered"})
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email_id = request.session.get('email')
            registration: Registration = create_registration(form, event, email_id)
            if registration_is_valid(registration, event):
                registration.save()
                user = create_user(request)
                populate_stats(user, event)
                reg = Registration.objects.get(email=email_id)
                context = {'user': user, 'registration': reg, 'event': event}
                logger.info('Registered new participant %s for event %s ' % (user.username, event.event_name))
                logger.debug('Registered new participant %s for event %s ' % (user.username, event.event_name))
                return render(request, 'events/reg_confirmation.html', context)
            else:
                err = 'Either dates are not valid or number of guests or number of days is invalid.'
                logger.error(err)
                logger.debug('>>>>>>>>>>>>>>>>>>>>' + err)
                context = {'user': create_user(request), 'form': form, 'event': event, 'err': err}
                return render(request, 'events/registration.html', context)
        else:
            logger.debug(form.errors)
            raise Http404('Invalid form')

    else:
        logger.debug('Request is GET')
        try:
            registration = Registration.objects.get(email__exact=user.email)
            deletable = check_deletable(event.event_date)
            context = {'registration': registration,
                       'attributes': registration.attributes(),
                       'user': user,
                       'deletable': deletable}
            if registration.is_deleted != 'Yes':
                return render(request, 'events/detail.html', context)
            else:
                context['message'] = 'Your registration is cancelled,please register again'
                context['event'] = event
                return render(request, 'events/detail.html', context)
        except Registration.DoesNotExist:
            reg_form = RegistrationForm(initial={'arrival_date': event.event_date})
            set_initial(reg_form, event, user.email)
            context = {'user': create_user(request), 'form': reg_form, 'event': event}
            return render(request, 'events/registration.html', context)


def detail(request):
    raise EnvironmentError


def edit(request, reg_id):
    if request.POST:
        reg_old = get_object_or_404(Registration, pk=reg_id)
        form = RegistrationForm(request.POST)
        if form.is_valid():
            reg_new = create_registration(form, reg_old.event, reg_old.email)
            reg_old.delete()
            reg_new.save()
            reg = Registration.objects.get(pk=reg_id + 1)
            event = Event.objects.get(pk=reg_new.event_id)
            context = {'user': create_user(request), 'event': event, 'registration': reg}
            return render(request, 'events/reg_confirmation.html', context)

    else:
        registration = get_object_or_404(Registration, pk=reg_id)
        event = registration.event
        reg_form = RegistrationForm(initial=registration.attributes())
        context = {'user': create_user(request), 'form': reg_form, 'event': event,
                   'registration': registration}
        return render(request, 'events/edit_registration.html', context)


def create_user(request):
    user = Login()
    user.email = request.session.get('email')
    user.username = request.session.get('username')
    if user.email and user.username:
        user_ = get_object_or_404(klass=Login, email__exact=user.email)
        return user_
    else:
        return None


def delete(request, reg_id):
    registration = get_object_or_404(Registration, pk=reg_id)
    registration.is_deleted = 'Yes'
    registration.save(update_fields=['is_deleted'])
    event = Event.objects.get(pk=registration.event_id)
    user = create_user(request)
    context = {'event': event, 'user': user}
    return render(request, 'events/delete_confirmation.html', context)


def deleted_view(request, event_id):
    login_ = create_user(request)
    deleted = Registration.objects.filter(is_deleted='Yes', event_id=event_id)
    return render(request, 'events/deleted_regs.html', {'deleted': deleted, 'user': login_})


def stats(request, event_id):
    stats_list = Registration_stats.objects.filter(event_id=event_id)
    l1 = []
    l2 = []
    for i in range(len(stats_list)):
        l1.append(str(stats_list[i].id))
        l2.append(stats_list[i].username)
    kv = dict(zip(l1, l2))
    context = {'user': create_user(request), 'event_id': event_id, 'stats': kv}
    return render(request, 'events/stats.html', context)


def get_event(event_id):
    try:
        return Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return None


msg_success = "Media Uploaded Successfully"
msg_warning = ''
msg = ''


def upload(request, event_id):
    global msg, msg_success, msg_warning
    logger.debug('File upload request received')
    login_ = create_user(request)
    event = Event.objects.get(pk=event_id)
    if request.POST:

        form = FileUploadForm(request.POST, request.FILES)
        files = request.FILES.getlist('files')
        print('form is valid and file length = %s %s' % (str(form.is_valid()), len(files)))
        global msg, msg_success, msg_warning
        if form.is_valid():
            for f in files:
                file: File_uploads = File_uploads()
                url = str(f)
                if url.__contains__('mp4') or \
                        url.__contains__('avi') or \
                        url.__contains__('mov') or \
                        url.__contains__('mpg') or \
                        url.__contains__('mpeg'):
                    logger.info('video file(s) is/are not saved')
                    msg_warning = 'video file(s) is/are not saved'
                    continue
                file.file_url = f
                file.event = event
                file.save()
                logger.debug('Media %s saved ' % str(file.file_url))
                form = FileUploadForm(initial={'event': event.event_name})
            logger.debug('message warning %s Length = %d' % (msg_warning, len(msg_warning)))
            if len(msg_warning) > 0:
                msg = msg_warning
            else:
                msg = msg_success
            return render(request, 'events/upload_media.html', {'user': login_, 'form': form,
                                                                'event': event, 'msg': msg})
        else:
            logger.error(form.errors)
            raise Http404('Upload failed.Contact administrator')
    else:
        form = FileUploadForm(initial={'event': event.event_name})
        logger.debug(form)
        return render(request, 'events/upload_media.html',
                      {'form': form, 'user': login_, 'event': event})


def registrations(request, event_id):
    login_ = create_user(request)
    if check_user_is_event_admin(login_, event_id=event_id):
        active_regs = Registration.objects.filter(is_deleted='No', event_id=event_id)
        return render(request, 'events/registrations.html', {'user': login_, 'active_regs': active_regs})
    raise Http404('File not found')


def display_media(request, event_id):
    uploaded_files = File_uploads.objects.filter(event_id=event_id)
    file_dict = {}
    for file in uploaded_files:
        url = str(file.file_url)
        if url.__contains__('mpg') or url.__contains__('avi') or url.__contains__('mov'):
            continue
        file_dict[file.id] = file.file_url
    logger.info('Urls of media => ', file_dict)
    context = {'files': file_dict, 'user': create_user(request)}
    return render(request, 'events/display_media.html', context)


def show_media(request, image_id):
    image = get_object_or_404(klass=File_uploads, pk=image_id)
    logger.info('retrieved image at %s' % image.file_url)
    image_url = image.file_url
    media_url = settings.MEDIA_URL
    file = media_url + str(image_url)
    image_title = str(image_url)[6:]
    context = {'file': file, 'title': image_title}
    return render(request, 'events/show_media.html', context)


def delete_media(request, event_id):
    files = File_uploads.objects.all()
    for file in files:
        file.delete()
        logger.info('deleted ', file.file_url)
    return render(request, 'events/login.html', {})


def export_csv(request, csv_id):
    if csv_id == 1:
        col_list = ['first_name', 'last_name', 'payment_amount', 'payment_ref',
                    'num_guests', 'num_days', 'pickup_reqd', 'mode_of_travel',
                    'arrival_date', 'departure_date', 'special_req', 'extended_tour', 'mobile']

        regs = Registration.objects.all().values_list('first_name', 'last_name', 'payment_amount', 'payment_ref',
                                                      'num_guests', 'num_days', 'pickup_reqd', 'mode_of_travel',
                                                      'arrival_date', 'departure_date', 'special_req', 'extended_tour',
                                                      'mobile'
                                                      )
        return create_csv(request, col_list, regs, 'registrations.csv')
    if csv_id == 2:
        col_list = ['first_name', 'last_name', 'payment_amount', 'payment_ref', 'num_guests', 'num_days']
        regs = Registration.objects.all().values_list('first_name', 'last_name', 'payment_amount', 'payment_ref',
                                                      'num_guests', 'num_days')
        return create_csv(request, col_list, regs, 'cancellations.csv')


def create_csv(request, columns_list, obj, filename):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;' + ' filename=' + filename
    writer = csv.writer(response)
    writer.writerow(columns_list)
    for val in obj:
        writer.writerow(val)
    return response


def logout(request):
    request.session.clear()
    return render(request, 'events/login.html', {'user': None})


def register_again(request, event_id):
    login_ = create_user(request)
    registration = Registration.objects.get(email__exact=login_.email, event_id=event_id)
    registration.delete()
    return render(request, 'events/registrations.html', {'user': login_})
