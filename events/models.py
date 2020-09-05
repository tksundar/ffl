from django.db import models
import datetime


class Login(models.Model):
    email = models.CharField(max_length=15)
    password = models.CharField(max_length=20)
    temp_password = models.CharField(max_length=10, default='')
    username = models.CharField(max_length=10, default=email)

    def __str__(self):
        return str({
            'email': self.email,
            'username': self.username,
            'id': self.id,
        })

    def create_login(self, data):
        self.username = data['username']
        self.email = data['email']
        return self


class Event(models.Model):
    event_name = models.CharField(max_length=25)
    event_venue = models.CharField(max_length=25)
    event_date = models.DateTimeField(default=None)
    event_description = models.CharField(max_length=100)
    event_link = models.URLField()
    event_managers = models.CharField(max_length=50, default=None)

    def __str__(self):
        return self.event_name


class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField(max_length=25)
    mobile = models.CharField(max_length=15)
    payment_amount = models.CharField(max_length=5)
    payment_ref = models.CharField(max_length=10)
    extended_tour = models.CharField(max_length=3)
    num_guests = models.IntegerField(default=1)
    num_days = models.IntegerField(default=2)
    mode_of_travel = models.CharField(max_length=5)
    arrival_date = models.DateTimeField(default=None)
    departure_date = models.DateTimeField(default=None)
    pickup_reqd = models.CharField(max_length=5)
    special_req = models.CharField(max_length=100)
    is_deleted = models.CharField(max_length=3, default='No')

    def __str__(self):
        return str(self.attributes())

    def attributes(self):
        return {
            'event': self.event.event_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'mobile': self.mobile,
            'payment_amount': self.payment_amount,
            'payment_ref': self.payment_ref,
            'extended_tour': self.extended_tour,
            'num_guests': str(self.num_guests),
            'num_days': str(self.num_days),
            'mode_of_travel': self.mode_of_travel,
            'arrival_date': str(self.arrival_date),
            'departure_date': str(self.departure_date),
            'pickup_reqd': self.pickup_reqd,
            'special_req': self.special_req
        }


class Registration_stats(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    username = models.CharField(max_length=10, default=None)

    def attributes(self):
        count = 0
        return {
            'id': self.id,
            'name': self.username

        }

    def __str__(self):
        return str(self.attributes())


class File_uploads(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    file_url = models.FileField(upload_to='media/', default=None)

    def __str__(self):
        return str(self.file_url)


class Event_Admin(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    admin = models.CharField(max_length=20)
