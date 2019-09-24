"""class_schedule_card URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from automatic_card.turn_views import *
from automatic_card.class_normal_views import *
from automatic_card.teacher_views import *
from automatic_card.other_views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home),
    path('start_input/', start_input),
    path('save_table_info/', receive_table_info),
    path('turn_subject/', turn_subject),
    path('save_subject_info/', receive_subject_info),
    path('delete_subject/', delete_subject),
    path('turn_teacher/', turn_teacher),
    path('save_teacher_group_info/', receive_teacher_group_info),
    path('save_grade_info/', receive_grade_info),
    path('save_teacher_info/', receive_teacher_info),
    path('update_teacher/', update_teacher_info),
    path('delete_teacher/', delete_teacher),
    path('turn_class/', turn_class),
    path('save_class_type_info/', receive_class_type_info),
    path('save_class_info/', receive_class_info),
    path('turn_class_hour/', turn_class_hour),
    path('save_subject_hour_info/', receive_subject_hour_info),
    path('turn_class_edit/', turn_class_edit),
    path('delete_class_normal/', delete_class_normal),
    path('update_class_normal/', update_class_normal),
]
