from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('delete_user/<int:pk>/', views.DeleteUser.as_view(), name='delete_user'),
    path('comment_section/<str:other_username>/', views.comment_section, name='comment_section'),
    path('payment_successful', views.payment_successful, name='payment_successful'),
    path('payment_cancelled', views.payment_cancelled, name='payment_cancelled'),
    path('stripe_webhook', views.stripe_webhook, name='stripe_webhook'),
    path('comment_history/', views.comment_history, name='comment_history'),
    path('charge/', views.charge, name='charge'),
    # path('create_payment_intent/', views.create_payment_intent, name='create_payment_intent'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)