from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from .models import Exam, Question, ChoiceOption, Answer, ExamResult
import json


class ExamListView(View):
    """考试列表视图"""

    def get(self, request):
        exams = Exam.objects.filter(is_active=True, start_date__lte=timezone.now())
        context = {
            'exams': exams,
            'current_time': timezone.now()
        }
        return render(request, 'exam_list.html', context)


class StartExamView(View):
    """开始考试视图"""

    def get(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id, is_active=True)

        # 获取考试题目
        questions = exam.questions.order_by('order')

        # 组织题目数据
        exam_data = []
        for question in questions:
            question_data = {
                'id': question.id,
                'type': question.question_type,
                'text': question.text,
                'score': question.score,
            }

            if question.question_type == 'choice':
                options = [
                    {'id': opt.id, 'text': opt.text}
                    for opt in question.options.all()
                ]
                question_data['options'] = options

            exam_data.append(question_data)

        context = {
            'exam': exam,
            'questions': exam_data,
            'duration_minutes': exam.duration
        }
        return render(request, 'exam_page.html', context)


class SubmitExamView(View):
    """提交考试视图"""

    def post(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)
        data = json.loads(request.body)

        # 获取会话标识
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key

        # 计算得分
        total_score = 0
        user_score = 0
        answers = {}

        for question_data in data['answers']:
            question_id = question_data['question_id']
            user_answer = question_data.get('answer', '')

            try:
                question = Question.objects.get(id=question_id)
                total_score += question.score

                try:
                    # 验证答案
                    if question.question_type == 'choice':
                        # 选择题：验证选项是否正确
                        selected_option = ChoiceOption.objects.get(id=user_answer)
                        if selected_option.is_correct:
                            user_score += question.score

                    elif question.question_type == 'fill':
                        # 填空题：验证答案是否匹配
                        correct_answer = question.answer.text.lower().strip()
                        if user_answer.lower().strip() == correct_answer:
                            user_score += question.score

                    elif question.question_type == 'judge':
                        # 判断题：验证答案是否正确
                        user_is_correct = (user_answer == 'true')
                        if user_is_correct == question.answer.is_correct:
                            user_score += question.score
                except (ValueError, ChoiceOption.DoesNotExist, Answer.DoesNotExist):
                    user_answer = ''

                # 保存用户答案
                answers[question_id] = user_answer

            except (Question.DoesNotExist, ChoiceOption.DoesNotExist):
                pass

        # 保存考试结果
        result = ExamResult.objects.create(
            exam=exam,
            session_key=session_key,
            score=user_score,
            total_score=total_score,
            answers=answers
        )

        return JsonResponse({
            'success': True,
            'score': user_score,
            'total_score': total_score,
            'result_id': result.id
        })


class ResultView(View):
    """考试结果视图"""

    def get(self, request, result_id):
        result = get_object_or_404(ExamResult, id=result_id)
        exam = result.exam

        # 获取题目和用户答案
        questions = []
        for question in exam.questions.order_by('order'):
            user_answer = result.answers.get(str(question.id), '')
            correct = False

            if question.question_type == 'choice':
                # 选择题
                try:
                    selected_option = ChoiceOption.objects.get(id=user_answer)
                    correct = selected_option.is_correct
                except (ValueError, ChoiceOption.DoesNotExist):
                    pass

                options = [
                    {'id': opt.id, 'text': opt.text, 'is_correct': opt.is_correct}
                    for opt in question.options.all()
                ]

                question_data = {
                    'type': 'choice',
                    'options': options,
                    'selected': user_answer
                }

            elif question.question_type == 'fill':
                # 填空题
                correct = (user_answer.lower().strip() == question.answer.text.lower().strip())
                question_data = {
                    'type': 'fill',
                    'correct_answer': question.answer.text,
                    'user_answer': user_answer
                }

            elif question.question_type == 'judge':
                # 判断题
                correct = (user_answer == str(question.answer.is_correct).lower())
                question_data = {
                    'type': 'judge',
                    'correct_answer': question.answer.is_correct,
                    'user_answer': user_answer
                }

            questions.append({
                'id': question.id,
                'text': question.text,
                'score': question.score,
                'correct': correct,
                'details': question_data
            })

        passed = result.score >= result.total_score * 0.6
        percent = round(result.score / result.total_score * 100, 2)

        context = {
            'result': result,
            'questions': questions,
            'passed': passed,
            'percent': percent
        }
        return render(request, 'exam_result.html', context)

