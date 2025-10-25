from django.shortcuts import render, get_object_or_404
from .models import LegalPage


def legal_page_detail(request, slug):
    page = get_object_or_404(LegalPage, slug=slug)
    return render(request, 'legal/legal_page_detail.html', {'page': page})