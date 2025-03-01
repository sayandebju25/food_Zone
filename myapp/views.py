"""
myapp/views.py
"""
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Dish, Booking
from datetime import datetime
from django.shortcuts import render, redirect
from .models import Category
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile


from myapp.forms import (
    RegisterForm, LoginForm, ProfileUpdateForm,
    OnlineOrderForm, BookTableForm, ProfileForm, CombinedProfileForm, CheckoutForm
)
from myapp.models import Contact, Dish, Team, Category, Order, Booking

@login_required
def download_invoice(request, order_id):
    # Get the order and ensure the logged-in user owns it
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Get phone number (assuming it's in the Order model)
    phone_number = order.phone_number if hasattr(order, 'phone_number') else order.user.profile.phone_number

    # Render the HTML template to a string, including the phone number
    html_string = render_to_string('invoice_pdf.html', {'order': order, 'phone_number': phone_number})
    
    # Generate the PDF
    pdf_file = HTML(string=html_string).write_pdf()

    # Return the response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    return response

def index(request):
    # Home page logic
    cats = Category.objects.all().order_by('name')
    dishes_by_cat = []
    for cat in cats:
        dishes_by_cat.append({
            'cat_id': cat.id,
            'cat_name': cat.name,
            'cat_img': cat.image,
            'items': list(cat.dish_set.all().values())
        })
    context = {
        'categories': cats,
        'menu': dishes_by_cat
    }
    return render(request, 'index.html', context)


def about(request):
    return render(request, 'about.html')


def contact_us(request):
    context = {}
    if request.method == "POST":
        name = request.POST.get("name")
        em = request.POST.get("email")
        sub = request.POST.get("subject")
        msz = request.POST.get("message")

        Contact.objects.create(name=name, email=em, subject=sub, message=msz)
        context['message'] = f"Dear {name}, Thanks for your time!"
    return render(request, 'contact.html', context)


def team_members(request):
    members = Team.objects.all().order_by('name')
    return render(request, 'team.html', {'team_members': members})


def all_dishes(request):
    context = {}
    dishes = Dish.objects.all()
    if "q" in request.GET:
        cat_id = request.GET.get("q")
        dishes = Dish.objects.filter(category__id=cat_id)
        context['dish_category'] = Category.objects.get(id=cat_id).name
    context['dishes'] = dishes
    return render(request, 'all_dishes.html', context)


def category_dishes(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    dishes = Dish.objects.filter(category=category)
    return render(request, 'category_dishes.html', {'category': category, 'dishes': dishes})


def dish_detail_redirect(request, id):
    # Shortcut function: /dish/<int:id>/ goes here
    return dish_detail(request, dish_id=id)


# -------------------------------------------------------------
# dish_detail: "Order Now" adds to cart, then redirects to checkout
# -------------------------------------------------------------
def dish_detail(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)

    if request.method == 'POST':
        # You can still use OnlineOrderForm if you want a quantity field
        # or just parse the quantity from POST.
        quantity = int(request.POST.get('quantity', 1))

        # 1) Retrieve or create the cart in session
        cart = request.session.get('cart', {})
        dish_id_str = str(dish_id)

        # 2) Add the item to the cart
        if dish_id_str in cart:
            cart[dish_id_str] += quantity
        else:
            cart[dish_id_str] = quantity

        # 3) Save cart back to session
        request.session['cart'] = cart
        request.session.modified = True

        # 4) Redirect to checkout
        return redirect('checkout')

    else:
        # If you want a quantity field, you can use OnlineOrderForm or a simpler form
        form = OnlineOrderForm()  # Not actually used to create an Order here
                                  # but might provide a 'quantity' field in the template.

    return render(request, 'dish.html', {
        'dish': dish,
        'form': form
    })


# -------------------------------------------------------------
# Profile & Registration/Authentication
# -------------------------------------------------------------


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    #bookings = Booking.objects.filter(user=request.user).order_by('date')
    #bookings = Booking.objects.filter(user=request.user).values('created_at')
    bookings = Booking.objects.filter(user=request.user).values('id', 'date', 'guests', 'created_at')

    
    orders_count = orders.count()
    bookings_count = bookings.count()

    # Show 3 newest orders unless 'show_orders' is set
    if request.GET.get('show_orders') == "all":
        displayed_orders = orders  # Show all orders
    else:
        displayed_orders = orders[:3]  # Show only the latest 3 orders

    # Show 3 newest bookings unless 'show_bookings' is set
    if request.GET.get('show_bookings') == "all":
        displayed_bookings = bookings  # Show all bookings
    else:
        displayed_bookings = bookings[:3]  # Show only the latest 3 bookings

    return render(request, 'profile.html', {
        'orders': displayed_orders,
        'bookings': displayed_bookings,
        'orders_count': orders_count,
        'bookings_count': bookings_count
    })



@login_required
def profile_update(request):
    user = request.user
    
    if request.method == 'POST':
        form = CombinedProfileForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            updated_user = form.save()
            
            # If password changed, re‐authenticate session
            # We can call update_session_auth_hash so user isn’t logged out
            new_password1 = form.cleaned_data.get('new_password1')
            if new_password1:
                update_session_auth_hash(request, updated_user)
            
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CombinedProfileForm(user=user)
    
    return render(request, 'profile_update.html', {'form': form})




def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('profile')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post', 'head', 'options']


# -------------------------------------------------------------
# Table Booking
# -------------------------------------------------------------
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Booking
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from .models import Category

from django.shortcuts import render
from .models import Category, Dish

def menu_view(request):
    categories = Category.objects.all()  # Fetch all categories
    menu = []

    for category in categories:
        items = Dish.objects.filter(category=category)  # Fetch dishes under each category
        menu.append({
            "cat_id": category.id,
            "cat_name": category.name,
            "cat_img": category.image.url if category.image else "",
            "items": list(items.values('id', 'name', 'ingredients', 'price', 'discounted_price', 'image'))
        })

    return render(request, 'book_table.html', {'menu': menu, 'categories': categories})


from django.utils import timezone
from datetime import timedelta

# @login_required
# def book_table_view(request):
#     # Generate available dates (next 3 days)
#     today = timezone.now().date()
#     available_dates = [
#         (today + timedelta(days=i)) for i in range(3)
#     ]
    
#     # Format dates for display and value
#     formatted_dates = [
#         (date.strftime('%Y-%m-%d'), date.strftime('%a, %d %b')) 
#         for date in available_dates
#     ]
    
#     guest_range = range(1, 11)
    
#     if request.method == "POST":
#         # Extract data from POST
#         date_str = request.POST.get("date")
#         guests = request.POST.get("guests")
#         meal_type = request.POST.get("meal_type")
#         slot = request.POST.get("slot")
        
#         # Parse date string to Date object
#         try:
#             date = datetime.strptime(date_str, '%Y-%m-%d').date()
#         except (ValueError, TypeError):
#             messages.error(request, "Invalid date selected.")
#             return redirect('book_table')
        
#         # Create Booking object
#         Booking.objects.create(
#             user=request.user,
#             date=date,
#             guests=guests,
#             meal_type=meal_type,
#             slot=slot
#         )
        
#         messages.success(request, "Table booked successfully!")
#         return redirect('booking_success')
    
#     # Fetch menu data
#     categories = Category.objects.prefetch_related('dish_set').all()
#     menu = []
#     for category in categories:
#         menu.append({
#             'category': category,
#             'dishes': category.dish_set.filter(is_available=True)
#         })
    
#     return render(request, 'book_table.html', {
#         'menu': menu,
#         'formatted_dates': formatted_dates,
#         'guest_range': guest_range,
#     })

# def booking_success(request):
#     return render(request, 'booking_success.html')


# -------------------------------------------------------------
# start_online_order (alternative to immediate cart approach)
# -------------------------------------------------------------
@login_required
def start_online_order(request):
    if request.method == 'POST':
        form = OnlineOrderForm(request.POST)
        if form.is_valid():
            dish_id = request.POST.get('dish_id')
            dish = get_object_or_404(Dish, id=dish_id)

            order = form.save(commit=False)
            order.user = request.user
            order.dish = dish
            order.status = 'Pending'
            order.address = request.user.profile.address  # Save the profile address
            order.save()

            return redirect('profile')
    else:
        initial_data = {}
        if hasattr(request.user, 'profile'):
            initial_data['delivery_address'] = request.user.profile.address
        form = OnlineOrderForm(initial=initial_data)

    return render(request, 'online_order.html', {'form': form})



# -------------------------------------------------------------
# Shopping Cart Flow
# -------------------------------------------------------------
@login_required
def add_to_cart(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    quantity = int(request.POST.get('quantity', 1))

    cart = request.session.get('cart', {})
    dish_id_str = str(dish_id)
    if dish_id_str in cart:
        cart[dish_id_str] += quantity
    else:
        cart[dish_id_str] = quantity

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('view_cart')


@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for dish_id_str, qty in cart.items():
        dish_id = int(dish_id_str)
        dish = get_object_or_404(Dish, id=dish_id)
        cost = dish.discounted_price if dish.discounted_price else dish.price
        subtotal = cost * qty
        total += subtotal
        items.append({
            'dish': dish,
            'quantity': qty,
            'subtotal': subtotal,
        })

    return render(request, 'cart.html', {
        'items': items,
        'total': total,
    })


@login_required
def remove_from_cart(request, dish_id):
    cart = request.session.get('cart', {})
    dish_id_str = str(dish_id)
    if dish_id_str in cart:
        del cart[dish_id_str]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('view_cart')


# -------------------------------------------------------------
# # Checkout + Payment
# # -------------------------------------------------------------
# # myapp/views.py
# @login_required
# def checkout(request):
#     cart = request.session.get('cart', {})
#     if not cart:
#         return redirect('view_cart')  # nothing to checkout

#     if request.method == 'POST':
#         form = CheckoutForm(request.POST)  # using the new form
#         if form.is_valid():
#             payment_method = form.cleaned_data['payment_method']
#             delivery_address = form.cleaned_data['delivery_address']
#             phone_number = form.cleaned_data['phone_number']

#             # Convert cart items into Order objects
#             for dish_id_str, qty in cart.items():
#                 dish_id = int(dish_id_str)
#                 dish = get_object_or_404(Dish, id=dish_id)

#                 # Create the order with address & phone
#                 order = Order.objects.create(
#                     user=request.user,
#                     dish=dish,
#                     quantity=qty,
#                     status='Pending' if payment_method == 'paypal' else 'Confirmed (COD)',
#                     delivery_address=delivery_address,
#                     phone_number=phone_number
#                 )

#             # Clear the cart
#             request.session['cart'] = {}
#             request.session.modified = True

#             # If you want to handle PayPal differently, do so here.
#             return redirect('payment_success')  # or payment_failure if something goes wrong
#     else:
#         form = CheckoutForm()

#     return render(request, 'checkout.html', {'form': form})


# def payment_success(request):
#     return render(request, 'payment_success.html')


# def payment_failure(request):
#     return render(request, 'payment_failure.html')

#now

# myapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
import paypalrestsdk
from .models import Dish, Order
from .forms import CheckoutForm

# Configure PayPal SDK
# Configure PayPal SDK (in views.py)
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET  # Fixed variable name
})


#     cart = request.session.get('cart', {})
    
#     # Check for empty cart
#     if not cart:
#         messages.warning(request, "Your cart is empty")
#         return redirect('view_cart')

#     # Validate cart items
#     valid_items = {}
#     invalid_items = []
#     total_amount = 0.0

#     for dish_id_str, qty in cart.items():
#         try:
#             dish_id = int(dish_id_str)
#             dish = Dish.objects.get(id=dish_id)
#             valid_items[dish_id] = {
#                 'dish': dish,
#                 'qty': qty,
#                 'price': dish.price
#             }
#             total_amount += dish.price * qty
#         except (ValueError, Dish.DoesNotExist):
#             invalid_items.append(dish_id_str)

#     if invalid_items:
#         # Handle invalid items
#         return redirect('view_cart')

#     if request.method == 'POST':
#         form = CheckoutForm(request.POST)
#         if form.is_valid():
#             payment_method = form.cleaned_data['payment_method']
#             delivery_address = form.cleaned_data['delivery_address']
#             phone_number = form.cleaned_data['phone_number']

#             if payment_method == 'paypal':
#                 # PayPal handling
#                 request.session['checkout_info'] = {
#                     'delivery_address': delivery_address,
#                     'phone_number': phone_number,
#                     'total_amount': total_amount
#                 }
                
#                 payment = paypalrestsdk.Payment({
#                     "intent": "sale",
#                     "payer": {"payment_method": "paypal"},
#                     "transactions": [{
#                         "amount": {
#                             "total": "{:.2f}".format(total_amount),
#                             "currency": "USD"
#                         },
#                         "description": "Food Order Payment",
#                         "item_list": {
#                             "items": [
#                                 {
#                                     "name": item['dish'].name,
#                                     "sku": str(dish_id),
#                                     "price": "{:.2f}".format(item['price']),
#                                     "currency": "USD",
#                                     "quantity": item['qty']
#                                 } for dish_id, item in valid_items.items()
#                             ]
#                         }
#                     }],
#                     "redirect_urls": {
#                         "return_url": request.build_absolute_uri(reverse('paypal_return')),
#                         "cancel_url": request.build_absolute_uri(reverse('paypal_cancel'))
#                     }
#                 })

#                 if payment.create():
#                     request.session['paypal_payment_id'] = payment.id
#                     approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
#                     return redirect(approval_url)
#                 else:
#                     messages.error(request, "Payment initialization failed")
#                     return redirect('payment_failure')

#             else:  # COD handling
#                 # Fix: Call create_orders directly, not via self
#                 create_orders(
#                     user=request.user,
#                     items=valid_items,
#                     address=delivery_address,
#                     phone=phone_number,
#                     status='Confirmed (COD)'
#                 )
#                 request.session['cart'] = {}
#                 messages.success(request, "Order placed successfully!")
#                 return redirect('payment_success')

#     else:
#         form = CheckoutForm(initial={
#             'delivery_address': request.user.profile.address if hasattr(request.user, 'profile') else '',
#             'phone_number': request.user.profile.contact_number if hasattr(request.user, 'profile') else ''
#         })

#     return render(request, 'checkout.html', {
#         'form': form,
#         'total_amount': total_amount
#     })


#     cart = request.session.get('cart', {})
    
#     if not cart:
#         messages.warning(request, "Your cart is empty")
#         return redirect('view_cart')

#     try:
#         valid_items = {}
#         total_amount = 0.0
#         invalid_items = []

#         for dish_id_str, qty in cart.items():
#             try:
#                 dish_id = int(dish_id_str)
#                 dish = Dish.objects.get(id=dish_id)
#                 valid_items[dish_id] = {
#                     'dish': dish,
#                     'qty': qty,
#                     'price': dish.price
#                 }
#                 total_amount += dish.price * qty
#             except (ValueError, Dish.DoesNotExist):
#                 invalid_items.append(dish_id_str)

#         if invalid_items:
#             return redirect('view_cart')

#         if request.method == 'POST':
#             form = CheckoutForm(request.POST)
#             if form.is_valid():
#                 # ... rest of your checkout logic ...

#         else:
#             form = CheckoutForm(initial={
#                 'delivery_address': request.user.profile.address if hasattr(request.user, 'profile') else '',
#                 'phone_number': request.user.profile.contact_number if hasattr(request.user, 'profile') else ''
#             })

#         return render(request, 'checkout.html', {
#             'form': form,
#             'total_amount': total_amount
#         })

#     except Exception as e:
#         logger.error(f"Checkout error: {str(e)}", exc_info=True)
#         messages.error(request, "An error occurred during checkout")
#         return redirect('view_cart')
# # Make sure this function is properly defined
#         def create_orders(user, items, address, phone, status):
#             for dish_id, item in items.items():
#                 Order.objects.create(
#                     user=user,
#                     dish=item['dish'],
#                     quantity=item['qty'],
#                     total_amount=item['price'] * item['qty'],
#                     status=status,
#                     delivery_address=address,
#                     phone_number=phone
#                 )
def checkout(request):
    cart = request.session.get('cart', {})
    
    # Check for empty cart
    if not cart:
        messages.warning(request, "Your cart is empty")
        return redirect('view_cart')

    # Validate cart items
    valid_items = {}
    invalid_items = []
    total_amount = 0.0

    for dish_id_str, qty in cart.items():
        try:
            dish_id = int(dish_id_str)
            dish = Dish.objects.get(id=dish_id)
            valid_items[dish_id] = {
                'dish': dish,
                'qty': qty,
                'price': dish.price
            }
            total_amount += dish.price * qty
        except (ValueError, Dish.DoesNotExist):
            invalid_items.append(dish_id_str)

    if invalid_items:
        # Handle invalid items
        return redirect('view_cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            delivery_address = form.cleaned_data['delivery_address']
            phone_number = form.cleaned_data['phone_number']

            if payment_method == 'paypal':
                # PayPal handling
                request.session['checkout_info'] = {
                    'delivery_address': delivery_address,
                    'phone_number': phone_number,
                    'total_amount': total_amount
                }
                
                payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {"payment_method": "paypal"},
                    "transactions": [{
                        "amount": {
                            "total": "{:.2f}".format(total_amount),
                            "currency": "USD"
                        },
                        "description": "Food Order Payment",
                        "item_list": {
                            "items": [
                                {
                                    "name": item['dish'].name,
                                    "sku": str(dish_id),
                                    "price": "{:.2f}".format(item['price']),
                                    "currency": "USD",
                                    "quantity": item['qty']
                                } for dish_id, item in valid_items.items()
                            ]
                        }
                    }],
                    "redirect_urls": {
                        "return_url": request.build_absolute_uri(reverse('paypal_return')),
                        "cancel_url": request.build_absolute_uri(reverse('paypal_cancel'))
                    }
                })

                if payment.create():
                    request.session['paypal_payment_id'] = payment.id
                    approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
                    return redirect(approval_url)
                else:
                    messages.error(request, "Payment initialization failed")
                    return redirect('payment_failure')

            else:  # COD handling
                # Fix: Call create_orders directly, not via self
                create_orders(
                    user=request.user,
                    items=valid_items,
                    address=delivery_address,
                    phone=phone_number,
                    status='Confirmed (COD)'
                )
                request.session['cart'] = {}
                messages.success(request, "Order placed successfully!")
                return redirect('payment_success')

    else:
        form = CheckoutForm(initial={
            'delivery_address': request.user.profile.address if hasattr(request.user, 'profile') else '',
            'phone_number': request.user.profile.contact_number if hasattr(request.user, 'profile') else ''
        })

    return render(request, 'checkout.html', {
        'form': form,
        'total_amount': total_amount
    })
def create_orders(user, items, address, phone, status):
            for dish_id, item in items.items():
                Order.objects.create(
                    user=user,
                    dish=item['dish'],
                    quantity=item['qty'],
                    total_amount=item['price'] * item['qty'],
                    status=status,
                    delivery_address=address,
                    phone_number=phone
                )

@login_required
def paypal_return(request):
    payment_id = request.session.get('paypal_payment_id')
    checkout_info = request.session.get('checkout_info')
    
    if not payment_id or not checkout_info:
        messages.error(request, "Invalid payment session")
        return redirect('payment_failure')

    payer_id = request.GET.get('PayerID')
    if not payer_id:
        messages.error(request, "Missing Payer ID")
        return redirect('payment_failure')

    # Execute PayPal payment
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        # Get validated cart items from session
        cart = request.session.get('cart', {})
        valid_items = {}
        for dish_id_str, qty in cart.items():
            dish_id = int(dish_id_str)
            dish = Dish.objects.get(id=dish_id)
            valid_items[dish_id] = {
                'dish': dish,
                'qty': qty,
                'price': dish.price
            }

        # Create orders
        create_orders(
            request.user,
            valid_items,
            checkout_info['delivery_address'],
            checkout_info['phone_number'],
            'Confirmed (PayPal)'
        )

        # Clear session data
        keys_to_delete = ['paypal_payment_id', 'checkout_info', 'cart']
        for key in keys_to_delete:
            if key in request.session:
                del request.session[key]
        request.session.modified = True

        messages.success(request, "Payment successful! Order confirmed.")
        return redirect('payment_success')
    else:
        messages.error(request, "Payment execution failed")
        return redirect('payment_failure')
    

@login_required
def paypal_cancel(request):
    # Clear payment session data
    keys_to_delete = ['paypal_payment_id', 'checkout_info']
    for key in keys_to_delete:
        if key in request.session:
            del request.session[key]
    request.session.modified = True
    messages.warning(request, "Payment cancelled")
    return redirect('view_cart')

def payment_success(request):
    return render(request, 'payment_success.html')

def payment_failure(request):
    return render(request, 'payment_failure.html')

#upto this 
from datetime import datetime, timedelta, time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import localtime, now

from .models import Booking, Category, Review
from .forms import ReviewForm



#     """Displays the table-booking form with next 7 days, lunch/dinner slots,
#        removes past times, and if lunch is chosen after 1:30 PM today,
#        shows a custom no-slots message.
#     """
#     # 1) Today's date/time in your TIME_ZONE
#     today = localtime(now()).date()
#     current_time = localtime(now()).time()

#     # 2) Next 7 days => (friendly_label, real_date)
#     next_7_days = [today + timedelta(days=i) for i in range(7)]
#     formatted_dates = [
#         (day.strftime('%a, %d %b'), day)
#         for day in next_7_days
#     ]

#     # 3) Determine user selections
#     if request.method == 'POST':
#         date_str = request.POST.get('date', formatted_dates[0][0])   # e.g. "Thu, 27 Feb"
#         meal_type = request.POST.get('meal_type', 'lunch')           # "lunch"/"dinner"
#     else:
#         date_str = request.GET.get('date', formatted_dates[0][0])
#         meal_type = request.GET.get('meal_type', 'lunch')

#     # Validate meal_type
#     if meal_type not in dict(Booking.MEAL_CHOICES):
#         meal_type = 'lunch'

#     # Convert friendly date_str (e.g. "Thu, 27 Feb") to a real date
#     selected_date_obj = None
#     for (friendly_str, real_date) in formatted_dates:
#         if friendly_str == date_str:
#             selected_date_obj = real_date
#             break

#     # If user tampered or no match => fallback to first
#     if not selected_date_obj:
#         date_str = formatted_dates[0][0]
#         selected_date_obj = formatted_dates[0][1]

#     # 4) Get the base time slots for that meal
#     time_slots = Booking.TIME_SLOTS.get(meal_type, [])

#     # We'll store a custom message if needed
#     custom_no_slots_message = None

#     # 5) Filter out past slots if date == today
#     if selected_date_obj == today:
#         if meal_type == 'lunch':
#             # If it's >= 1:30 PM => remove all lunch slots
#             lunch_cutoff = time(13, 30)
#             if current_time >= lunch_cutoff:
#                 time_slots = []
#                 custom_no_slots_message = (
#                     "No available slot today for lunch. "
#                     "Try another date or dinner."
#                 )
#             else:
#                 # Otherwise, remove only the slots already past
#                 filtered = []
#                 for slot_tuple in time_slots:
#                     slot_time_str = slot_tuple[0]  # e.g. "1:00 PM"
#                     slot_time = datetime.strptime(slot_time_str, "%I:%M %p").time()
#                     if slot_time > current_time:
#                         filtered.append(slot_tuple)
#                 time_slots = filtered

#         elif meal_type == 'dinner':
#             # Filter out dinner times already past
#             filtered = []
#             for slot_tuple in time_slots:
#                 slot_time_str = slot_tuple[0]
#                 slot_time = datetime.strptime(slot_time_str, "%I:%M %p").time()
#                 if slot_time > current_time:
#                     filtered.append(slot_tuple)
#             time_slots = filtered

#     # 6) Handle POST: booking or review
#     review_form = ReviewForm(request.POST or None)

#     if request.method == 'POST':
#         if 'booking_submit' in request.POST:
#             # Must be logged in
#             if not request.user.is_authenticated:
#                 messages.error(request, "You must be logged in to book a table.")
#                 return redirect('book_table')

#             try:
#                 slot = request.POST.get('slot', '').strip()
#                 guests = int(request.POST.get('guests', 1))
#                 if not slot:
#                     messages.error(request, "Please select a time slot.")
#                     return redirect('book_table')

#                 Booking.objects.create(
#                     user=request.user,
#                     date=selected_date_obj,
#                     guests=guests,
#                     meal_type=meal_type,
#                     slot=slot
#                 )
#                 messages.success(request, "Table booked successfully!")
#                 return redirect('booking_success')

#             except ValueError:
#                 messages.error(request, "Invalid guest number.")
#             except Exception as e:
#                 messages.error(request, f"Error processing booking: {str(e)}")
#             return redirect('book_table')

#         elif 'review_submit' in request.POST and review_form.is_valid():
#             review = review_form.save(commit=False)
#             if request.user.is_authenticated:
#                 review.user = request.user
#                 review.name = f"{request.user.first_name} {request.user.last_name}".strip()
#             review.save()
#             messages.success(request, "Review submitted for approval!")
#             return redirect('book_table')

#     # 7) Prepare context
#     menu_categories = Category.objects.prefetch_related('dish_set').all()
#     reviews = Review.objects.filter(approved=True).order_by('-created_at')[:10]
#     guest_range = range(1, 11)

#     context = {
#         "formatted_dates": formatted_dates,
#         "selected_date_str": date_str,
#         "selected_meal": meal_type,
#         "time_slots": time_slots,
#         "custom_no_slots_message": custom_no_slots_message,  # our custom message
#         "menu_categories": menu_categories,
#         "guest_range": guest_range,
#         "reviews": reviews,
#         "review_form": review_form,
#         "meal_choices": Booking.MEAL_CHOICES,
#     }
#     return render(request, "book_table.html", context)
from datetime import datetime, timedelta, time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import localtime, now

from .models import Booking, Category, Review
from .forms import ReviewForm

from datetime import datetime, timedelta, time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import localtime, now

#     """Shows lunch/dinner slots with cutoffs for both:
#        - Lunch => no slot if current_time >= 1:30 PM
#        - Dinner => no slot if current_time >= 10:00 PM
#     """
#     # 1) Today's date/time
#     today = localtime(now()).date()
#     current_time = localtime(now()).time()

#     # 2) Next 7 days => (friendly_label, real_date)
#     next_7_days = [today + timedelta(days=i) for i in range(7)]
#     formatted_dates = [
#         (day.strftime('%a, %d %b'), day)
#         for day in next_7_days
#     ]

#     # 3) Determine user selection
#     if request.method == 'POST':
#         date_str = request.POST.get('date', formatted_dates[0][0])   # e.g. "Thu, 27 Feb"
#         meal_type = request.POST.get('meal_type', 'lunch')           # "lunch"/"dinner"
#     else:
#         date_str = request.GET.get('date', formatted_dates[0][0])
#         meal_type = request.GET.get('meal_type', 'lunch')

#     # Validate meal_type
#     if meal_type not in dict(Booking.MEAL_CHOICES):
#         meal_type = 'lunch'

#     # Convert friendly date_str back to date
#     selected_date_obj = None
#     for (friendly_str, real_date) in formatted_dates:
#         if friendly_str == date_str:
#             selected_date_obj = real_date
#             break

#     # Fallback if no match
#     if not selected_date_obj:
#         date_str = formatted_dates[0][0]
#         selected_date_obj = formatted_dates[0][1]

#     # 4) Base time slots
#     time_slots = Booking.TIME_SLOTS.get(meal_type, [])

#     # Custom no-slots message if cutoff is reached
#     custom_no_slots_message = None

#     # 5) Filter out past slots if selected date == today
#     if selected_date_obj == today:
#         if meal_type == 'lunch':
#             lunch_cutoff = time(13, 30)  # 1:30 PM
#             if current_time >= lunch_cutoff:
#                 time_slots = []
#                 custom_no_slots_message = (
#                     "No available slot today for lunch. "
#                     "Try another date or dinner."
#                 )
#             else:
#                 # Filter out only slots that are already past
#                 filtered = []
#                 for slot_tuple in time_slots:
#                     slot_time_str = slot_tuple[0]
#                     slot_time = datetime.strptime(slot_time_str, "%I:%M %p").time()
#                     if slot_time > current_time:
#                         filtered.append(slot_tuple)
#                 time_slots = filtered

#         elif meal_type == 'dinner':
#             dinner_cutoff = time(22, 0)  # 10:00 PM
#             if current_time >= dinner_cutoff:
#                 time_slots = []
#                 custom_no_slots_message = (
#                     "No available slot today for dinner. "
#                     "Try another date or lunch."
#                 )
#             else:
#                 # Filter out only slots that are already past
#                 filtered = []
#                 for slot_tuple in time_slots:
#                     slot_time_str = slot_tuple[0]
#                     slot_time = datetime.strptime(slot_time_str, "%I:%M %p").time()
#                     if slot_time > current_time:
#                         filtered.append(slot_tuple)
#                 time_slots = filtered

#     # 6) Handle form submissions
#     review_form = ReviewForm(request.POST or None)
#     if request.method == "POST":
#         if 'booking_submit' in request.POST:
#             if not request.user.is_authenticated:
#                 messages.error(request, "You must be logged in to book a table.")
#                 return redirect('book_table')

#             try:
#                 slot = request.POST.get('slot', '').strip()
#                 guests = int(request.POST.get('guests', 1))
#                 if not slot:
#                     messages.error(request, "Please select a time slot.")
#                     return redirect('book_table')

#                 # Create booking
#                 Booking.objects.create(
#                     user=request.user,
#                     date=selected_date_obj,
#                     guests=guests,
#                     meal_type=meal_type,
#                     slot=slot
#                 )
#                 messages.success(request, "Table booked successfully!")
#                 return redirect('booking_success')

#             except ValueError:
#                 messages.error(request, "Invalid guest number.")
#             except Exception as e:
#                 messages.error(request, f"Error processing booking: {str(e)}")
#             return redirect('book_table')

#         elif 'review_submit' in request.POST and review_form.is_valid():
#             review = review_form.save(commit=False)
#             if request.user.is_authenticated:
#                 review.user = request.user
#                 review.name = (f"{request.user.first_name} {request.user.last_name}").strip()
#             review.save()
#             messages.success(request, "Review submitted for approval!")
#             return redirect('book_table')

#     # 7) Render
#     menu_categories = Category.objects.prefetch_related('dish_set').all()
#     reviews = Review.objects.filter(approved=True).order_by('-created_at')[:10]
#     guest_range = range(1, 11)

#     context = {
#         "formatted_dates": formatted_dates,
#         "selected_date_str": date_str,
#         "selected_meal": meal_type,
#         "time_slots": time_slots,
#         "custom_no_slots_message": custom_no_slots_message,
#         "menu_categories": menu_categories,
#         "guest_range": guest_range,
#         "reviews": reviews,
#         "review_form": review_form,
#         "meal_choices": Booking.MEAL_CHOICES,
#     }
#     return render(request, "book_table.html", context)
from datetime import datetime, timedelta, time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import localtime, now


# def book_table_view(request):
#     """
#     Shows lunch/dinner slots for the next 7 days.
#     Removes lunch slots if it's >= 1:30 PM, 
#     Removes dinner slots if it's >= 10:00 PM (only for 'today').
#     """
#     # Print server time for debugging
#     debug_now = localtime(now())
#     print("DEBUG: current server time =>", debug_now)

#     # 1) Today
#     today = debug_now.date()
#     current_time = debug_now.time()

#     # 2) Next 7 days => (friendly_label, date_obj)
#     next_7_days = [today + timedelta(days=i) for i in range(7)]
#     formatted_dates = [
#         (d.strftime('%a, %d %b'), d) for d in next_7_days
#     ]

#     # 3) Determine user selections
#     if request.method == "POST":
#         selected_date_str = request.POST.get("date", formatted_dates[0][0])
#         selected_meal     = request.POST.get("meal_type", "lunch")
#     else:
#         selected_date_str = request.GET.get("date", formatted_dates[0][0])
#         selected_meal     = request.GET.get("meal_type", "lunch")

#     valid_meals = dict(Booking.MEAL_CHOICES).keys()  # {"lunch", "dinner"}
#     if selected_meal not in valid_meals:
#         selected_meal = "lunch"

#     # Convert the friendly date string back to a real date
#     selected_date_obj = None
#     for (friendly_str, real_date) in formatted_dates:
#         if friendly_str == selected_date_str:
#             selected_date_obj = real_date
#             break
#     if not selected_date_obj:
#         selected_date_str = formatted_dates[0][0]
#         selected_date_obj = formatted_dates[0][1]

#     # 4) Base time slots
#     time_slots = Booking.TIME_SLOTS.get(selected_meal, [])
#     custom_no_slots_message = None

#     # 5) Define cutoff times
#     lunch_cutoff  = time(13, 30)  # 1:30 PM
#     dinner_cutoff = time(22,  0)  # 10:00 PM

#     # 6) If it's 'today', apply cutoff logic
#     if selected_date_obj == today:
#         if selected_meal == "lunch":
#             if current_time >= lunch_cutoff:
#                 # No lunch slots
#                 time_slots = []
#                 custom_no_slots_message = (
#                     "No available slot for lunch today. "
#                     "Try dinner or another date."
#                 )
#             else:
#                 # Filter out past lunch times
#                 filtered = []
#                 for slot_tuple in time_slots:
#                     slot_time_obj = datetime.strptime(slot_tuple[0], "%I:%M %p").time()
#                     if slot_time_obj > current_time:
#                         filtered.append(slot_tuple)
#                 time_slots = filtered

#         elif selected_meal == "dinner":
#             if current_time >= dinner_cutoff:
#                 # No dinner slots
#                 time_slots = []
#                 custom_no_slots_message = (
#                     "No available slot for dinner today. "
#                     "Try another date or lunch tomorrow."
#                 )
#             else:
#                 # Filter out past dinner times
#                 filtered = []
#                 for slot_tuple in time_slots:
#                     slot_time_obj = datetime.strptime(slot_tuple[0], "%I:%M %p").time()
#                     if slot_time_obj > current_time:
#                         filtered.append(slot_tuple)
#                 time_slots = filtered

#     # 7) Handle "Book Now"
#     if request.method == "POST" and "booking_submit" in request.POST:
#         slot_chosen = request.POST.get("slot", "").strip()
#         if not slot_chosen:
#             messages.error(request, "Please select a time slot.")
#         else:
#             messages.success(request, "Table booked successfully!")
#             return redirect("booking_success")

#     context = {
#         "formatted_dates": formatted_dates,
#         "selected_date_str": selected_date_str,
#         "selected_meal": selected_meal,
#         "time_slots": time_slots,
#         "custom_no_slots_message": custom_no_slots_message,
#         "guest_range": range(1, 11),
#         "meal_choices": Booking.MEAL_CHOICES,
#     }
#     return render(request, "book_table.html", context)


from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import localtime, now
from datetime import datetime, timedelta, time
from .models import Booking

def book_table_view(request):
    # Print server time for debugging
    debug_now = localtime(now())
    print("DEBUG: current server time =>", debug_now)

    # 1) Today
    today = debug_now.date()
    current_time = debug_now.time()

    # 2) Next 7 days => (friendly_label, date_obj)
    next_7_days = [today + timedelta(days=i) for i in range(7)]
    formatted_dates = [
        (d.strftime('%a, %d %b'), d) for d in next_7_days
    ]

    # 3) Determine user selections
    if request.method == "POST":
        selected_date_str = request.POST.get("date", formatted_dates[0][0])
        selected_meal = request.POST.get("meal_type", "lunch")
    else:
        selected_date_str = request.GET.get("date", formatted_dates[0][0])
        selected_meal = request.GET.get("meal_type", "lunch")

    valid_meals = dict(Booking.MEAL_CHOICES).keys()  # {"lunch", "dinner"}
    if selected_meal not in valid_meals:
        selected_meal = "lunch"

    # Convert the friendly date string back to a real date
    selected_date_obj = None
    for (friendly_str, real_date) in formatted_dates:
        if friendly_str == selected_date_str:
            selected_date_obj = real_date
            break
    # Fallback if not found
    if not selected_date_obj:
        selected_date_str = formatted_dates[0][0]
        selected_date_obj = formatted_dates[0][1]

    # 4) Base time slots
    time_slots = Booking.TIME_SLOTS.get(selected_meal, [])
    custom_no_slots_message = None

    # 5) Define cutoff times
    lunch_cutoff  = time(13, 30)  # 1:30 PM
    dinner_cutoff = time(22,  0)  # 10:00 PM

    # 6) If it's 'today', apply cutoff logic
    if selected_date_obj == today:
        if selected_meal == "lunch":
            if current_time >= lunch_cutoff:
                # No lunch slots
                time_slots = []
                custom_no_slots_message = (
                    "No available slot for lunch today. "
                    "Try dinner or another date."
                )
            else:
                # Filter out past lunch times
                filtered = []
                for slot_tuple in time_slots:
                    slot_time_obj = datetime.strptime(slot_tuple[0], "%I:%M %p").time()
                    if slot_time_obj > current_time:
                        filtered.append(slot_tuple)
                time_slots = filtered

        elif selected_meal == "dinner":
            if current_time >= dinner_cutoff:
                # No dinner slots
                time_slots = []
                custom_no_slots_message = (
                    "No available slot for dinner today. "
                    "Try another date or lunch tomorrow."
                )
            else:
                # Filter out past dinner times
                filtered = []
                for slot_tuple in time_slots:
                    slot_time_obj = datetime.strptime(slot_tuple[0], "%I:%M %p").time()
                    if slot_time_obj > current_time:
                        filtered.append(slot_tuple)
                time_slots = filtered

    # 7) Handle "Book Now"
    if request.method == "POST" and "booking_submit" in request.POST:
        slot_chosen = request.POST.get("slot", "").strip()
        guests_chosen = request.POST.get("guests", "1")

        if not slot_chosen:
            messages.error(request, "Please select a time slot.")
        else:
            # ✅ Actually create the Booking record
            try:
                new_booking = Booking.objects.create(
                    user=request.user,                # Must be logged in
                    date=selected_date_obj,
                    meal_type=selected_meal,
                    slot=slot_chosen,
                    guests=int(guests_chosen),
                )
                messages.success(request, "Table booked successfully!")
                return redirect("booking_success")
            except Exception as e:
                messages.error(request, f"Booking error: {str(e)}")

    context = {
        "formatted_dates": formatted_dates,
        "selected_date_str": selected_date_str,
        "selected_meal": selected_meal,
        "time_slots": time_slots,
        "custom_no_slots_message": custom_no_slots_message,
        "guest_range": range(1, 11),
        "meal_choices": Booking.MEAL_CHOICES,
    }
    return render(request, "book_table.html", context)


def booking_success(request):
    """Simple success page."""
    return render(request, "booking_success.html")

def menu_view(request):
    food_items = Dish.objects.filter(is_available=True, is_deleted=False)
    return render(request, "book_table.html", {"food_items": food_items})
