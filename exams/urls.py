from django.urls import path
from . import views

app_name = 'exams'  # 定义命名空间

urlpatterns = [
    path('', views.ExamListView.as_view(), name='exam_list'),
    path('start/<int:exam_id>/', views.StartExamView.as_view(), name='start_exam'),
    path('submit/<int:exam_id>/', views.SubmitExamView.as_view(), name='submit_exam'),
    path('result/<int:result_id>/', views.ResultView.as_view(), name='view_result'),
]