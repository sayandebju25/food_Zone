# myapp/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import password_validation

from django.contrib.auth.models import User
from .models import Order,Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import password_validation
from myapp.models import Profile

class CombinedProfileForm(forms.Form):
    # ---- A) User fields ----
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    
    # ---- B) Profile fields ----
    contact_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    profile_pic = forms.ImageField(required=False)
    
    # ---- C) Password fields (optional) ----
    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput,
        required=False
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
        required=False
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput,
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        """Pass the current request.user into the form so we can show initial data."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Fill in initial data from the user model
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            
            # Fill in from Profile
            if hasattr(self.user, 'profile'):
                self.fields['contact_number'].initial = self.user.profile.contact_number
                self.fields['address'].initial = self.user.profile.address
                # There's no built-in "initial" for ImageField, so we usually just show blank

    def clean(self):
        """Check that new_password1/new_password2 match, etc."""
        cleaned_data = super().clean()
        
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 or new_password2:
            # If user is attempting a password change, check match
            if new_password1 != new_password2:
                self.add_error('new_password2', "New passwords did not match.")
            else:
                # Optionally run Django’s built-in password validators
                try:
                    password_validation.validate_password(new_password1, self.user)
                except forms.ValidationError as e:
                    self.add_error('new_password1', e)
        
        return cleaned_data
    
    def save(self):
        """Save changes to User & Profile & possibly set a new password."""
        user = self.user
        if not user:
            return None
        
        # A) Update user model fields
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        
        # B) Update or create the profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.contact_number = self.cleaned_data['contact_number']
        profile.address = self.cleaned_data['address']
        
        if self.cleaned_data.get('profile_pic'):
            profile.profile_pic = self.cleaned_data['profile_pic']
        
        profile.save()
        
        # C) Handle password changes
        old_password = self.cleaned_data.get('old_password')
        new_password1 = self.cleaned_data.get('new_password1')
        
        # If user filled in new_password1, we check old_password
        if new_password1:
            # Confirm old_password is correct
            if not user.check_password(old_password):
                # If you want to raise an error if old password is invalid, do so
                # e.g. self.add_error('old_password', "Old password is incorrect.")
                # or do nothing but skip changing password
                pass
            else:
                # Set new password
                user.set_password(new_password1)
                user.save()
        
        return user

class BookTableForm(forms.Form):
    date_time = forms.DateTimeField()
    guests = forms.IntegerField()

class OnlineOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['quantity','delivery_address']

# NEW: Payment method form
# myapp/forms.py
from django import forms

class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = (
        ('paypal', 'PayPal'),
        ('cod', 'Cash on Delivery'),
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        label='Payment Method'
    )
    delivery_address = forms.CharField(
        label='Delivery Address',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text='Please provide your full address (including house/apt number, street, etc.).'
    )
    phone_number = forms.CharField(
        label='Phone Number',
        max_length=20,
        required=True,
        help_text='We will use this number to contact you if needed.'
    )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_pic', 'contact_number', 'address']

        
class OnlineOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'dish', 'quantity', 'delivery_address']

from .models import Review



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'comment']  # Must match model fields
        labels = {
            'name': 'Your Name',
            'rating': 'Rating',
            'comment': 'Your Review'
        }