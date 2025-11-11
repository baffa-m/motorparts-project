from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from .models import Manufacturer, Part, Category

# Enhanced Home View with Featured Content
class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['featured_parts'] = Part.objects.filter(
            is_active=True,
            stock_quantity__gt=0
        ).select_related('manufacturer', 'category')[:4]
        
        context['all_categories'] = Category.objects.filter(is_active=True).order_by('name')[:4]
        
        context['categories'] = Category.objects.filter(is_active=True)[:4]
        
        context['manufacturers'] = Manufacturer.objects.filter(is_active=True)[:4]
        
        return context


# Parts Listing View (This is now the products page, not homepage)
class PartsListView(ListView):
    template_name = "parts/parts/index.html"
    model = Part
    paginate_by = 12
    context_object_name = "parts"
    
    def get_queryset(self):
        queryset = Part.objects.filter(is_active=True).select_related('category', 'manufacturer')
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(part_number__icontains=search_query)
            )
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by manufacturer
        manufacturer_slug = self.request.GET.get('manufacturer')
        if manufacturer_slug:
            queryset = queryset.filter(manufacturer__slug=manufacturer_slug)
        
        # Filter by condition
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        # Filter by vehicle type
        vehicle_type = self.request.GET.get('vehicle_type')
        if vehicle_type:
            queryset = queryset.filter(vehicle_type=vehicle_type)
        
        # Filter by price range
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Sort
        sort_by = self.request.GET.get('sort', '-created_at')
        allowed_sorts = ['price', '-price', 'name', '-name', 'created_at', '-created_at']
        if sort_by in allowed_sorts:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_categories'] = Category.objects.filter(is_active=True).order_by('name')[:4]
        context['categories'] = Category.objects.filter(is_active=True)
        context['manufacturers'] = Manufacturer.objects.filter(is_active=True)
        context['conditions'] = Part.CONDITION_CHOICES
        context['vehicle_types'] = Part.VEHICLE_TYPE_CHOICES
        return context


# Manufacturer List View
class ManufacturerListView(ListView):
    template_name = "parts/manufacturer/listing.html"
    model = Manufacturer
    paginate_by = 12
    context_object_name = 'manufacturers'
    
    def get_queryset(self):
        return Manufacturer.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_categories'] = Category.objects.filter(is_active=True).order_by('name')[:4]
        return context


# Part Detail View
class PartDetailView(DetailView):
    template_name = "parts/parts/detail.html"
    model = Part
    context_object_name = "part"
    
    def get_queryset(self):
        return Part.objects.filter(is_active=True).select_related('category', 'manufacturer')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_categories'] = Category.objects.filter(is_active=True).order_by('name')[:4]
        # Get related parts from same category
        context['related_parts'] = Part.objects.filter(
            category=self.object.category,
            is_active=True,
            stock_quantity__gt=0
        ).exclude(pk=self.object.pk).select_related('manufacturer')[:4]
        return context


class CategoryListView(ListView):
    template_name = "parts/category/listing.html"
    model = Category
    paginate_by = 12
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_categories'] = Category.objects.filter(is_active=True).order_by('name')[:4]
        return context
