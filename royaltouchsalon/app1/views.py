from django.shortcuts import render,redirect,get_object_or_404
from django.core.mail import send_mail
from app1.forms import ContactForm
from django.contrib import messages
from .models import Booking
from django.conf import settings
import datetime


  

def index(request):
    return render(request,'index.html')

def services(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        service = request.POST.get('service')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        message = request.POST.get('message')

        #validation for appointment date
        try:
            appointment_date = datetime.datetime.strptime(appointment_date, '%Y-%m-%d').date()
            appointment_time = datetime.datetime.strptime(appointment_time, '%H:%M').time()

            if appointment_date < datetime.date.today():
                messages.warning(request,"Appointment date cannot be in the past!")
                return redirect('services')
            
            #check if time slot is already booked
            if Booking.objects.filter(appointment_date = appointment_date,appointment_time=appointment_time,service=service).exists():
                messages.warning(request,"This time slot is not available. Please choose another one")
            else:
                booking = Booking(
                    customer_name=customer_name,
                    email=email,
                    phone = phone,
                    service= service,
                    appointment_date = appointment_date,
                    appointment_time = appointment_time,
                    message=message
                )
                booking.save()

                #send mail notification to the admin
                send_mail(
                    subject="New home service booking",
                    message = f"new booking by {booking.customer_name} for {booking.service} on {booking.appointment_date} at {booking.appointment_time}.\n\nDetails:\n"
                    f"Name: {booking.customer_name}\nEmail: {booking.email}\nPhone: {booking.phone}\nService: {booking.service}\nMessage: {booking.message}",
                    from_email = settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL],
                )

                messages.success(request,"Your appointment has been booked successfully!")
                return redirect('services')
        
        except ValueError:
            messages.error(request,"invalid date or time format.")
        
    return render(request,'services.html')
    
def about(request):
    return render(request,'about.html')

def gallery(request):
    return render(request,'gallery.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            send_mail(
                f'New contact message from {contact.name}',
                contact.message,contact.email,['khushisen9001@gmail.com'],fail_silently=False,
            )
            messages.success(request,'Your message has been sent succesfully!')
            return redirect('contact')
    else:
        form=ContactForm()
    return render(request,'contact.html',{'form':form})



