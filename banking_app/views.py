from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.views import View
from .forms import ContactForm
from .models import UserMessage 
from django.contrib import messages

from django.utils import timezone
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage


class HomeView(TemplateView):
    template_name = 'home/home.html'


class ContactUsView(View):
    template_name = 'home/contact.html'

    def get(self, request):
        form = ContactForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            UserMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )

            current_datetime = timezone.now()

            template_name = "emails/contact_us.html"
            context = {
                "message": message, 
                'subject': subject.title(), 
                'current_datetime': current_datetime, 
                'name':name.title(),
                'email': email,
                }

            email_body = render_to_string(template_name, context)

            email = EmailMessage(
                    subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL, 
                    ['iqbal.ilham.77@gmail.com'], 
                )
            
            email.content_subtype = "html"

            email.send()

            # send_mail(
            #     f'Contact Us: {subject}',
            #     f'From: {name} ({email})\n\n{message}',
            #     email,
            #     ['iqbal.ilham.77@gmail.com'],
            #     fail_silently=False,
            # )

            messages.success(request, 'Your message has been sent successfully, We will contact you back soon. Thank you!')
            
            return redirect('banking_app:contact_us')

        return render(request, self.template_name, {'form': form})