from django.contrib import admin
from django.utils.html import format_html
from myapp.models import Contact, Category, Dish, Profile, Order, Review, Booking

admin.site.site_header = "FoodZone | Admin"

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'subject', 'added_on', 'is_approved']
    list_filter = ['is_approved', 'added_on']
    search_fields = ['name', 'email', 'subject']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'added_on', 'updated_on']
    search_fields = ['name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'contact_number', 'updated_on']
    search_fields = ['user__username', 'contact_number']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'dish', 'quantity', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'dish__name', 'status')
    ordering = ('-created_at',)
    actions = ['mark_as_delivered']

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='Delivered')
    mark_as_delivered.short_description = "Mark selected orders as Delivered"

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discounted_price', 'is_available', 'is_deleted')
    list_filter = ('category', 'is_available', 'is_deleted')
    search_fields = ('name', 'category__name')
    actions = ['restore_dish']

    def restore_dish(self, request, queryset):
        queryset.update(is_deleted=False)
    restore_dish.short_description = "Restore selected dishes"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'rating', 'approved', 'created_at')
    list_filter = ('rating', 'approved')
    search_fields = ('name', 'user__username')


from django.contrib import admin
from django.utils.html import format_html
from .models import RestaurantPhoto, Booking,Team

@admin.register(RestaurantPhoto)
class RestaurantPhotoAdmin(admin.ModelAdmin):
    list_display = ('thumbnail_preview', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('description',)
    
    def thumbnail_preview(self, obj):
        return format_html(f'<img src="{obj.image.url}" style="max-height: 100px;" />')
    thumbnail_preview.short_description = "Preview"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'meal_type', 'slot', 'guests')
    list_filter = ('date', 'meal_type')
    search_fields = ('user__username', 'date')
    date_hierarchy = 'date'

@admin.register(Team) 
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'designation', 'added_on', 'updated_on')
    list_filter = ('added_on', 'updated_on')
    search_fields = ('name', 'designation')
    date_hierarchy = 'added_on'
       