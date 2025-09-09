from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from .models import Manufacturer, Part, Category

# Create your views here.


class HomeView(TemplateView):
    template_name = 'parts/index.html'