from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='main_page'),  # Main page at root URL
    path('index/', views.index, name='index'),    # Detection page
    path('video_feed/', views.video_feed, name='video_feed'),
    path('stop_camera/', views.stop_camera, name='stop_camera'),
    path('detected_student_info/', views.detected_student_info, name='detected_student_info'),
    path('student_list/', views.student_list, name='student_list'),
]
