from django.db import models
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Booking(models.Model):
    HOME_SERVICE_CHOICES = [
        ('professional_makeup','Professional Makeup'),
        ('manicure_pedicure','Manicure Pedicure'),
        ('body_treatment','Body Treatment'),
        ('hair_treatment','Hair Treatment'),
    ]
    customer_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    service = models.CharField(max_length = 20, choices = HOME_SERVICE_CHOICES)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    message = models.TextField(blank = True,null=True)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer_name} - {self.service} on {self.appointment_date} at {self.appointment_time}'
    


