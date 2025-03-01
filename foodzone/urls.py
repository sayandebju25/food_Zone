# foodzone/urls.py
from django.contrib import admin
from django.urls import path, include
from myapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_us, name='contact'),
    path('team/', views.team_members, name='team'),
    path('dishes/', views.all_dishes, name='all_dishes'),
    path('dish/<int:id>/', views.dish_detail_redirect, name='dish'),
    path('category/<int:category_id>/', views.category_dishes, name='category_dishes'),

    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.profile_update, name='update_profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('register/', views.register_view, name='register'),

    path('dish/<int:dish_id>/add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:dish_id>/', views.remove_from_cart, name='remove_from_cart'),
    #erly
    #path('checkout/', views.checkout, name='checkout'),
    #path('payment_success/', views.payment_success, name='payment_success'),
    #path('payment_failure/', views.payment_failure, name='payment_failure'),
    #now
    path('checkout/', views.checkout, name='checkout'),
    path('paypal/return/', views.paypal_return, name='paypal_return'),
    path('paypal/cancel/', views.paypal_cancel, name='paypal_cancel'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failure, name='payment_failure'),


    path('book-table/', views.book_table_view, name='book_table'),
    path('booking-success/', views.booking_success, name='booking_success'),
    #path('booking_success/', views.booking_success, name='booking_success'),
    path('order/<int:order_id>/download-invoice/', views.download_invoice, name='download_invoice'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
