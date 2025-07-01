# serializers.py - 简化序列化逻辑
from rest_framework import serializers
from exam.models import Exam, Paper, Grade


class PaperSerializer(serializers.ModelSerializer):
    """试卷序列化器"""

    class Meta:
        model = Paper
        fields = ['id', 'name', 'score', 'choice_number', 'judge_number', 'fill_number']


class ExamSerializer(serializers.ModelSerializer):
    """考试序列化器"""
    # 直接使用试卷ID进行关联，避免不必要的嵌套
    paper_id = serializers.PrimaryKeyRelatedField(
        queryset=Paper.objects.all(),
        source='paper',
        write_only=True
    )

    class Meta:
        model = Exam
        fields = ['id', 'name', 'exam_date', 'total_time', 'tips', 'paper', 'paper_id']
        read_only_fields = ['paper']  # 确保paper字段只读，避免在创建时传入复杂数据

    def to_representation(self, instance):
        """自定义表示方法，返回时包含试卷基本信息"""
        representation = super().to_representation(instance)
        representation['paper'] = {
            'id': instance.paper.id,
            'name': instance.paper.name,
            'total_score': instance.paper.score
        }
        return representation


class GradeSerializer(serializers.ModelSerializer):
    """成绩序列化器"""
    # 考试ID用于创建成绩时传入
    exam_id = serializers.PrimaryKeyRelatedField(
        queryset=Exam.objects.all(),
        source='exam',
        write_only=True
    )

    class Meta:
        model = Grade
        fields = ['id', 'score', 'student_name', 'create_time', 'exam', 'exam_id']
        read_only_fields = ['exam']  # 确保exam字段只读

    def to_representation(self, instance):
        """自定义表示方法，返回时包含考试基本信息"""
        representation = super().to_representation(instance)
        representation['exam'] = {
            'id': instance.exam.id,
            'name': instance.exam.name,
            'date': instance.exam.exam_date
        }
        return representation