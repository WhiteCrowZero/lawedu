# 项目根目录下的 urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

# 导入视图
from . import views
from exams import views as exams_views
from video import views as video_views

urlpatterns = [
    # 1. 管理员后台
    path('admin/', admin.site.urls),

    # 2. 考试系统应用
    path('exams/', include('exams.urls')),

    # 3. 视频应用
    path('video/', include('video.urls')),

    # 4. API 应用
    path('api/', include('model_api.urls')),

    # 5. 错误处理页面
    path('404/', views.handler404, name='404'),
    path('500/', views.handler500, name='500'),

    # 6. 首页配置
    # 使用静态HTML作为首页
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('us/', TemplateView.as_view(template_name='us.html'), name='us'),
]

# 7. 静态文件和媒体文件服务（仅开发环境）
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
