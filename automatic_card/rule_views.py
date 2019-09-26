from automatic_card.models import *
from django.http import JsonResponse
import json
import uuid
from django.db.models import Q


def get_teacher_rule(request):
    group = TeacherGroup.objects.get(group_name=request.POST.get('group'))
    teacher = Teacher.objects.filter(teacher_group=group)[0]
    teacher_rules = TeacherRule.objects.filter(teacher=teacher)
    items = []
    if len(teacher_rules) > 0:
        for teacher_rule in teacher_rules:
            item = {'x': teacher_rule.column_card.column_index,
                    'y': teacher_rule.row_card.row_index,
                    'type': teacher_rule.item}
            items.append(item)
        return JsonResponse({'status': 200, 'color_cells': items})
    else:
        return JsonResponse({'status': 300})


def receive_teacher_rule(request):
    data = json.loads(request.body.decode('utf-8'))
    group = TeacherGroup.objects.get(group_name=data['group'])
    teachers = Teacher.objects.filter(teacher_group=group)
    for teacher in teachers:
        teacher_rules = TeacherRule.objects.filter(teacher=teacher)
        for teacher_rule in teacher_rules:
            teacher_rule.teacher.remove(teacher)
    for item in data['items']:
        if not item['type'] == '0':
            row_card = RowCard.objects.get(row_name=item['y'])
            column_card = ColumnCard.objects.get(column_index=item['x'])
            try:
                teacher_rule = TeacherRule.objects.get(Q(column_card=column_card),
                                                       Q(row_card=row_card))
                teacher_rule.item = item['type']
                teacher_rule.save()
            except BaseException:
                teacher_rule = TeacherRule(str(uuid.uuid1()).replace('-', ''),
                                           row_card.row_id,
                                           column_card.column_id, item['type'])
                teacher_rule.save()
            for teacher in teachers:
                teacher_rule.teacher.add(teacher)
    return JsonResponse({'status': 200})


def get_class_rule(request):
    grade_type = request.POST.get('grade_type')
    grade_or_type = grade_type.split('|')
    grade = Grade.objects.get(grade_name=grade_or_type[0])
    items = []
    if len(grade_or_type) == 1:
        grade_rule = GradeRule.objects.filter(grade=grade)
        if len(grade_rule) == 0:
            return JsonResponse({'status': 300})
        else:
            for class_normal_rule in grade_rule:
                item = {'x': class_normal_rule.column_card.column_index,
                        'y': class_normal_rule.row_card.row_index,
                        'type': class_normal_rule.item}
                items.append(item)
            return JsonResponse({'status': 200, 'item_cells': items})
    else:
        class_type = ClassType.objects.get(type_name=grade_or_type[1])
        class_normal = ClassNormal.objects.filter(
            class_grade=grade).filter(class_type=class_type)[0]
    class_normal_rules = ClassNormalRule.objects.filter(class_normal=
                                                        class_normal)
    if len(class_normal_rules) == 0:
        return JsonResponse({'status': 300})
    else:
        for class_normal_rule in class_normal_rules:
            item = {'x': class_normal_rule.column_card.column_index,
                    'y': class_normal_rule.row_card.row_index,
                    'type': class_normal_rule.item}
            items.append(item)
        return JsonResponse({'status': 200, 'item_cells': items})


def receive_class_rule(request):
    data = json.loads(request.body.decode('utf-8'))
    grade_or_type = data['grade_or_type'].split('|')
    grade = Grade.objects.get(grade_name=grade_or_type[0])
    if len(grade_or_type) == 1:
        class_normals = ClassNormal.objects.filter(class_grade=grade)
        for grade_rule in grade.graderule_set.all():
            grade.graderule_set.remove(grade_rule)
        for item in data['items']:
            row_card = RowCard.objects.get(row_name=item['y'])
            column_card = ColumnCard.objects.get(column_index=item['x'])
            try:
                grade_rule = GradeRule.objects.get(Q(row_card=row_card),
                                                   Q(column_card=column_card),
                                                   Q(item=item['type']))
            except BaseException:
                grade_rule = GradeRule(str(uuid.uuid1()).replace('-', ''),
                                       row_card.row_id,
                                       column_card.column_id,
                                       item['type'])
                grade_rule.save()
            grade_rule.grade.add(grade)
    else:
        class_type = ClassType.objects.get(type_name=grade_or_type[1])
        class_normals = ClassNormal.objects.filter(
            class_grade=grade).filter(class_type=class_type)
    class_hour = {}
    for item in data['items']:
        if item['type'] in class_hour:
            class_hour[item['type']] += 1
        else:
            class_hour[item['type']] = 1
    class_normal_hour = {}
    for subject_class in class_normals[0].subjectclassnormal_set.all():
        if subject_class.subject.subject_name in class_normal_hour:
            class_normal_hour[subject_class.subject.subject_name] += \
                subject_class.subject_number
        else:
            class_normal_hour[subject_class.subject.subject_name] = \
                subject_class.subject_number
    error_subject_name = []
    error_hour = []
    for key in class_hour.keys():
        if key in class_normal_hour:
            if class_hour[key] > class_normal_hour[key]:
                error_hour.append({'subject_name': str(key)})
        else:
            error_subject_name.append({'subject_name': str(key)})
    if len(error_subject_name) > 0 or len(error_hour) > 0:
        return JsonResponse({'status': 300, 'high_hour': error_hour,
                             'no_subject': error_subject_name})
    for class_normal in class_normals:
        for old_class_rule in class_normal.classnormalrule_set.all():
            class_normal.classnormalrule_set.remove(old_class_rule)
    for item in data['items']:
        row_card = RowCard.objects.get(row_name=item['y'])
        column_card = ColumnCard.objects.get(column_index=item['x'])
        try:
            class_rule = ClassNormalRule.objects.get(Q(row_card=row_card),
                                                     Q(column_card=column_card),
                                                     Q(item=item['type']))
        except BaseException:
            class_rule = ClassNormalRule(str(uuid.uuid1()).replace('-', ''),
                                         row_card.row_id, column_card.column_id,
                                         item['type'])
            class_rule.save()
        for class_normal in class_normals:
            class_rule.class_normal.add(class_normal)
    return JsonResponse({'status': 200})

