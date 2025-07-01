from django.contrib import admin
from .models import Exam, Question, ChoiceOption, Answer, ExamResult


class ChoiceOptionInline(admin.TabularInline):
    """选择题选项内联"""
    model = ChoiceOption
    extra = 1


class AnswerInline(admin.StackedInline):
    """答案内联"""
    model = Answer
    extra = 0
    max_num = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    """考试管理"""
    list_display = ('name', 'start_date', 'end_date', 'duration', 'is_active')
    list_filter = ('is_active', 'start_date')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('时间设置', {
            'fields': ('start_date', 'end_date', 'duration')
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """题目管理"""
    list_display = ('text', 'exam', 'question_type', 'score', 'order')
    list_filter = ('exam', 'question_type')
    search_fields = ('text',)
    inlines = [ChoiceOptionInline, AnswerInline]
    fieldsets = (
        (None, {
            'fields': ('exam', 'question_type', 'text', 'score', 'order')
        }),
    )

    # 根据题目类型动态显示字段
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.question_type == 'choice':
            fieldsets = (
                (None, {
                    'fields': ('exam', 'question_type', 'text', 'score', 'order')
                }),
            )
        return fieldsets


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    """考试成绩管理"""
    list_display = ('exam', 'session_key', 'score', 'total_score', 'created_at')
    list_filter = ('exam', 'created_at')
    search_fields = ('session_key',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('exam', 'session_key', 'score', 'total_score', 'answers')
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )

    # 禁止修改成绩记录
    def has_change_permission(self, request, obj=None):
        return False