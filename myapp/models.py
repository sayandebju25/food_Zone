from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Contact(models.Model):
    name = models.CharField(max_length=250)
    email = models.EmailField()
    subject = models.CharField(max_length=250)
    message = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Contact Table"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="categories/%Y/%m/%d")
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    image = models.ImageField(upload_to="team")
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Dish(models.Model):
    name = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to='dishes/%Y/%m/%d')
    ingredients = models.TextField()
    details = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_index=True)
    price = models.FloatField()
    discounted_price = models.FloatField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()

    def delete(self):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profiles/%Y/%m/%d', null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(blank=True)
    updated_on = models.DateTimeField(auto_now=True)

    def is_complete(self):
        return bool(self.contact_number and self.address)

    def __str__(self):
        return f"{self.user.username} ({'Complete' if self.is_complete() else 'Incomplete'})"

# myapp/models.py
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed (COD)', 'Confirmed (COD)'),
        ('Delivered', 'Delivered'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    delivery_address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)  # <--- new field
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.dish and self.quantity:
            self.total_amount = self.dish.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MaxValueValidator  # Add this import


class RestaurantPhoto(models.Model):
    CATEGORY_CHOICES = [
        ('all', 'All'),
        ('ambience', 'Ambience'),
        ('food', 'Food'),
    ]
    
    image = models.ImageField(upload_to='restaurant_photos/%Y/%m/%d/')
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='all',
        db_index=True  # Added for better filtering performance
    )
    description = models.CharField(
        max_length=255, 
        blank=True,
        null=True  # Allow NULL in database
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Restaurant Photos"
        db_table = 'myapp_restaurantphoto'  # Explicit table name

    def __str__(self):
        return f"{self.get_category_display()} - {self.created_at.strftime('%Y-%m-%d')}"

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

from django.utils.timezone import localtime, now
from datetime import timedelta
from django.utils.timezone import localtime, now

class Booking(models.Model):
    MEAL_CHOICES = [
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
    ]
    
    TIME_SLOTS = {
        "lunch": [
            ('12:00 PM', '12:00 PM'),
            ('12:30 PM', '12:30 PM'),
            ('1:00 PM', '1:00 PM'),
            ('1:30 PM', '1:30 PM'),
        ],
        "dinner": [
            ('7:00 PM', '7:00 PM'),
            ('7:30 PM', '7:30 PM'),
            ('8:00 PM', '8:00 PM'),
            ('9:00 PM', '9:00 PM')
        ]
    }


    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    date = models.DateField(db_index=True)
    guests = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    meal_type = models.CharField(
        max_length=10, 
        choices=MEAL_CHOICES, 
        default='lunch'
    )
    slot = models.CharField(
        max_length=20
    )
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date', 'meal_type', 'slot']),
        ]
        unique_together = ['date', 'slot', 'user']

    def clean(self):
        """Validate that the slot matches the selected meal type."""
        valid_slots = self.TIME_SLOTS.get(self.meal_type, [])
        slot_values = [s[0] for s in valid_slots]

        if self.slot not in slot_values:
            raise ValidationError(f"Invalid time slot '{self.slot}' for meal type '{self.meal_type}'.")

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.date} {self.slot} ({self.meal_type})"
    
class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Review by {self.name} ({self.rating} stars)"



