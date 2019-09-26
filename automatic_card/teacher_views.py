from automatic_card.models import *
from django.http import JsonResponse
import json
import uuid
from django.db.models import Q


def receive_teacher_group_info(request):
    data = request.POST.get('teacher_group_name')
    try:
        teacher_group = TeacherGroup.objects.get(group_name=data)
        return JsonResponse({'status': 300})
    except BaseException:
        teacher_group = TeacherGroup(str(uuid.uuid1()).replace('-', ''), data)
        teacher_group.save()
        return JsonResponse({'status': 200})


def receive_grade_info(request):
    data = request.POST.get('grade_name')
    try:
        grade = Grade.objects.get(grade_name=data)
        return JsonResponse({'status': 300})
    except BaseException:
        grade = Grade(str(uuid.uuid1()).replace('-',''), data)
        grade.save()
        return JsonResponse({'status': 200})


def receive_teacher_info(request):
    data = json.loads(request.body.decode('utf-8'))
    grade = Grade.objects.get(grade_name=data['teacher_grade'])
    try:
        teacher = Teacher.objects.get(Q(teacher_name=data['teacher_name']),
                                      Q(teacher_grade=grade))
        return JsonResponse({'status': 300})
    except BaseException:
        subjects = data['subject_items']
        group = TeacherGroup.objects.get(group_name=data['teacher_group'])
        teacher = Teacher(str(uuid.uuid1()).replace('-', ''),
                          data['teacher_name'], group.group_id,
                          grade.grade_id)
        teacher.save()
        for one_subject in subjects:
            teacher_subject = Subject.objects.get(subject_name=one_subject)
            teacher_subject.teacher.add(teacher)
        return JsonResponse({'status': 200})


def update_teacher_info(request):
    data = json.loads(request.body.decode('utf-8'))
    subjects = data['subjects']
    teacher_name = data['teacher_name']
    old_grade = Grade.objects.get(grade_name=data['old_grade'])
    grade = Grade.objects.get(grade_name=data['grade'])
    teacher_group = TeacherGroup.objects.get(group_name=data['teacher_group'])
    teacher = Teacher.objects.get(Q(teacher_name=teacher_name),
                                  Q(teacher_grade=old_grade))
    for subject in teacher.subject_set.all():
        teacher.subject_set.remove(subject)
    for subject_name in subjects:
        subject = Subject.objects.get(subject_name=subject_name.strip())
        teacher.subject_set.add(subject)
    teacher.teacher_grade_id = grade.grade_id
    teacher.teacher_group_id = teacher_group.group_id
    teacher.save()
    return JsonResponse({'status': 200})


def delete_teacher(request):
    data = json.loads(request.body.decode('utf-8'))
    grade = Grade.objects.get(grade_name=data['grade'])
    teacher = Teacher.objects.get(Q(teacher_name=data['teacher_name']),
                                  Q(teacher_grade=grade))
    teacher.delete()
    return JsonResponse({'status': 200})