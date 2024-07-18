from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='detection_index'), #URL parttern for detect app to view
    path('video_feed/', views.video_feed, name='video_feed'),
    path('stop_camera/', views.stop_camera, name='stop_camera'),
    path('student_list/', views.student_list, name='student_list'),
    # path('detected_student_info/', views.detetct_that_student, name='detected_student_info'),
]
