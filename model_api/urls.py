#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Name   : urls.py
Author      : wzw
Date Created: 2025/6/27
Description : Add your script's purpose here.
"""
# ai/urls.py
from django.urls import path
from .views import upload_audio, upload_image, infer, set_role, role_list, model_index

app_name = 'model_api'

urlpatterns = [
    path('model_api/set_role/', set_role, name='set_role'),
    path('model_api/roles/', role_list, name='role_list'),
    path('model_api/upload/audio/', upload_audio, name='upload_audio'),
    path('model_api/upload/image/', upload_image, name='upload_image'),
    path('model_api/infer/', infer, name='model_infer'),
    path('index/', model_index, name='index'),
]
