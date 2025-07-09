# filter.py - 仅保留必要的过滤功能
import django_filters
from exams.models import Exam

class ExamFilter(django_filters.rest_framework.FilterSet):
    """考试日期范围过滤器"""
    date_min = django_filters.DateFilter(field_name='exam_date', lookup_expr='gte', label="开始日期")
    date_max = django_filters.DateFilter(field_name='exam_date', lookup_expr='lte', label="结束日期")

    class Meta:
        model = Exam
        fields = ['date_min', 'date_max']