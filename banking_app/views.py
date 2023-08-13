from django.views.generic import TemplateView
from django.shortcuts import render
from django.core.mail import send_mail
from django.views import View
from .forms import ContactForm
from .models import UserMessage 


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

            user_message = UserMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )

            send_mail(
                f'Contact Us: {subject}',
                f'From: {name} ({email})\n\n{message}',
                email,
                ['iqbal.ilham.77@gmail.com'],
                fail_silently=False,
            )

            return render(request, 'home/contact.html')

        return render(request, self.template_name, {'form': form})