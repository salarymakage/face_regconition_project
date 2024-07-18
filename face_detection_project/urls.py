from django.contrib import admin
from django.urls import path, include
from detection import views  # Import views from the detection app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),  # Add this line for the root URL
    path('detection/', include('detection.urls')),  # Include URLs from the detection app
]
