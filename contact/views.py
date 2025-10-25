from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ContactInquiry
from .forms import ContactForm
from properties.models import Property

def contact_form(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            property_id = request.POST.get('property_id')
            if property_id:
                prop = get_object_or_404(Property, pk=property_id)
                inquiry.property = prop
                # TODO: Send email to agent
            inquiry.save()
            messages.success(request, "Your inquiry has been sent successfully! We'll get back to you soon.")
            return redirect('contact:contact_form')
    else:
        form = ContactForm()
    return render(request, 'contact/contact_form.html', {'form': form})
