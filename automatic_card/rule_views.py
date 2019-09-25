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
    teachers = group.teacher_set.all()
    for item in data['items']:
        row_card = RowCard.objects.get(row_name=item['y'])
        column_card = ColumnCard.objects.get(column_index=item['x'])
        teacher_rule = TeacherRule(str(uuid.uuid1()).replace('-', ''),
                                   row_card.row_id, column_card.column_id,
                                   item['type'])
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
            grade_rule = ''
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
        for class_normal in class_normals:
            for class_rule in class_normal.classnormalrule_set.all():
                class_normal.classnormalrule_set.remove(class_rule)
    for item in data['items']:
        row_card = RowCard.objects.get(row_name=item['y'])
        column_card = ColumnCard.objects.get(column_index=item['x'])
        class_rule = ''
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

