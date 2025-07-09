from django.db import models
from django.utils import timezone


class Exam(models.Model):
    """考试模型"""
    name = models.CharField("考试名称", max_length=100)
    description = models.TextField("考试描述", blank=True)
    duration = models.PositiveIntegerField("考试时长(分钟)", default=60)
    start_date = models.DateTimeField("开始时间", default=timezone.now)
    end_date = models.DateTimeField("结束时间", null=True, blank=True)
    is_active = models.BooleanField("是否启用", default=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    """基础题目模型"""
    QUESTION_TYPES = (
        ('choice', '选择题'),
        ('fill', '填空题'),
        ('judge', '判断题'),
    )

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField("题目类型", max_length=10, choices=QUESTION_TYPES)
    # answer = models.OneToOneField(Answer, on_delete=models.SET_NULL, null=True, blank=True, related_name='question')
    text = models.TextField("题目内容")
    score = models.PositiveSmallIntegerField("分值", default=1)
    order = models.PositiveSmallIntegerField("排序", default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.exam}: {self.text[:50]}"


class ChoiceOption(models.Model):
    """选择题选项"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField("选项内容", max_length=200)
    is_correct = models.BooleanField("是否正确答案", default=False)

    def __str__(self):
        return self.text


class Answer(models.Model):
    """答案模型（用于填空题和判断题）"""
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer')
    text = models.CharField("正确答案", max_length=200, blank=True)  # 用于填空题
    is_correct = models.BooleanField("是否正确", default=True)  # 用于判断题

    def __str__(self):
        return self.text if self.text else ("正确" if self.is_correct else "错误")


class ExamResult(models.Model):
    """考试结果模型"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    session_key = models.CharField("会话标识", max_length=40)
    score = models.PositiveSmallIntegerField("得分")
    total_score = models.PositiveSmallIntegerField("总分")
    answers = models.JSONField("作答记录")  # 存储题目ID和选择的答案
    created_at = models.DateTimeField("完成时间", auto_now_add=True)

    def __str__(self):
        return f"{self.session_key} - {self.score}/{self.total_score}"