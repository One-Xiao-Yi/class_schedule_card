from automatic_card.models import *
from django.shortcuts import render
import random
import copy
from django.db.models import Q
import uuid
import json
from django.http import JsonResponse


def make_card(request):
    # 一个班课程表结构
    card_dict = {}
    Card.objects.all().delete()
    # 制作空表结构
    for column_card in ColumnCard.objects.all():
        row_dict = {}
        for row_card in RowCard.objects.all():
            row_dict[row_card.row_index] = ' '
        card_dict[column_card.column_index] = row_dict

    for grade in Grade.objects.all():
        # 每个老师所教课程
        teacher_subject_dict = {}
        # 每一个课程对应的老师
        subject_teacher_dict = {}
        teacher_card = {}
        # 获取每个老师所教授的课程、教授每个课程的教师
        for teacher in grade.teacher_set.all():
            teacher_subject_dict[teacher.teacher_name] = []
            teacher_card[teacher.teacher_name] = copy.deepcopy(card_dict)
            for teacher_subject in teacher.subject_set.all():
                teacher_subject_dict[teacher.teacher_name].append(
                    teacher_subject.subject_name)
                if teacher_subject.subject_name not in subject_teacher_dict:
                    subject_teacher_dict[teacher_subject.subject_name] = []
                    subject_teacher_dict[teacher_subject.subject_name].append(
                        teacher.teacher_name)
                else:
                    subject_teacher_dict[teacher_subject.subject_name].append(
                        teacher.teacher_name)
            for teacher_rule in teacher.teacherrule_set.all():
                if teacher_rule.item == -1:
                    teacher_card[teacher.teacher_name][teacher_rule.column_card.column_index][teacher_rule.row_card.row_index] = ''

        # 每一个课程对应的班
        subject_class_dict = {}
        # 每一个班对应的课程
        class_subject_dict = {}
        class_card = {}
        # 获取班级所需教授课程、需教授的每个课程的班级
        for class_normal in grade.classnormal_set.all():
            class_card[class_normal.class_name] = copy.deepcopy(card_dict)
            class_subject_dict[class_normal.class_name] = []
            headmaster = class_normal.head_master
            same_grade = True
            if not headmaster.teacher_grade == grade:
                same_grade = False
            for subject_hour in class_normal.subjectclassnormal_set.all():
                if subject_hour.subject_number > 0:
                    if same_grade and subject_hour.subject in headmaster.subject_set.all():
                        class_subject_dict[class_normal.class_name].append(
                            {'subject_name': subject_hour.subject.subject_name,
                             'subject_number': subject_hour.subject_number,
                             'teacher': headmaster.teacher_name})
                    else:
                        class_subject_dict[class_normal.class_name].append(
                            {'subject_name': subject_hour.subject.subject_name,
                             'subject_number': subject_hour.subject_number,
                             'teacher': ''})
                        if subject_hour.subject.subject_name not in subject_class_dict:
                            subject_class_dict[
                                subject_hour.subject.subject_name] = []
                        subject_class_dict[subject_hour.subject.subject_name] \
                            .append(class_normal.class_name)

            for class_rule in class_normal.classnormalrule_set.all():
                class_card[class_normal.class_name][class_rule.column_card.column_index][class_rule.row_card.row_index] = class_rule.item

        class_subject_only_dict = {}
        for key in class_subject_dict:
            class_subject_only_dict[key] = {}
            for subject_hour in class_subject_dict[key]:
                if subject_hour['teacher'] == '':
                    class_subject_only_dict[key][subject_hour['subject_name']] = ''

        class_subject_number = {}
        for key in class_subject_only_dict:
            for inner_key in class_subject_only_dict[key]:

                if inner_key in class_subject_number:
                    class_subject_number[inner_key] += 1
                else:
                    class_subject_number[inner_key] = 1
        teacher_list = {}
        for key in subject_teacher_dict:
            teacher_list[key] = []
            if key in class_subject_number:
                teacher_class_number = int(class_subject_number[key] / len(subject_teacher_dict[key]))
                rest = class_subject_number[key] % len(subject_teacher_dict[key])
                for teacher_name in subject_teacher_dict[key]:
                    for l in range(teacher_class_number):
                        teacher_list[key].append(teacher_name)
                for index in range(rest):
                    teacher_list[key].append(subject_teacher_dict[key][index])
        for key in subject_class_dict:
            if key in teacher_list:
                for class_index in range(len(subject_class_dict[key])):
                    for index in range(len(class_subject_dict[subject_class_dict[key][class_index]])):
                        if class_subject_dict[subject_class_dict[key][class_index]][index]['subject_name'] == key:
                            class_subject_dict[subject_class_dict[key][class_index]][index]['teacher'] = teacher_list[key][class_index]
        old_class_hour = {}
        for key in class_card:
            old_class_hour[key] = {}
            for old_subject_hour in class_subject_dict[key]:
                old_class_hour[key][old_subject_hour['subject_name']] = old_subject_hour['subject_number']
            for column_key in class_card[key]:
                for row_key in class_card[key][column_key]:
                    if class_card[key][column_key][row_key] in old_class_hour[key]:
                        old_class_hour[key][class_card[key][column_key][row_key]] -= 1

        for key in class_subject_dict:
            no_teacher_subject = {}
            for subject in class_subject_dict[key]:
                class_rest = []
                for column_key in class_card[key]:
                    for row_key in class_card[key][column_key]:
                        if class_card[key][column_key][row_key] == ' ':
                            class_rest.append([column_key, row_key])
                teacher = subject['teacher']
                if teacher:
                    teacher_rest = []
                    for column_key in teacher_card[teacher]:
                        for row_key in teacher_card[teacher][column_key]:
                            if teacher_card[teacher][column_key][row_key]:
                                teacher_rest.append([column_key, row_key])
                    same_point = []
                    for item in class_rest:
                        if item in teacher_rest:
                            same_point.append(item)
                    for i in range(old_class_hour[key][subject['subject_name']]):
                        random.shuffle(same_point)
                        current_point = same_point.pop()
                        teacher_card[teacher][current_point[0]][current_point[1]] = ''
                        class_card[key][current_point[0]][current_point[1]] = subject['subject_name']
                else:
                    no_teacher_subject[subject['subject_name']] = copy.deepcopy(old_class_hour[key][subject['subject_name']])

            for subject_name in no_teacher_subject:
                no_subject_point = []
                for column_key in class_card[key]:
                    for row_key in class_card[key][column_key]:
                        if class_card[key][column_key][row_key] == ' ':
                            no_subject_point.append([column_key, row_key])
                if len(no_subject_point) > 2:
                    random.shuffle(no_subject_point)
                if no_teacher_subject[subject_name] > 0:
                    for i in range(no_teacher_subject[subject_name]):
                        pop_point = no_subject_point.pop()
                        class_card[key][pop_point[0]][
                            pop_point[1]] = subject_name
        for key in class_subject_dict:
            class_normal = ClassNormal.objects.get(class_name=key)
            class_normal.teacher.remove(class_normal.teacher.all())
            for subject_hour in class_subject_dict[key]:
                if subject_hour['teacher']:
                    teacher = Teacher.objects.get(Q(teacher_grade=grade), Q(teacher_name=subject_hour['teacher']))
                    class_normal.teacher.add(teacher)
        for key in class_card:
            for column_key in class_card[key]:
                for row_key in class_card[key][column_key]:
                    class_normal = ClassNormal.objects.get(class_name=key)
                    row = RowCard.objects.get(row_index=row_key)
                    column = ColumnCard.objects.get(column_index=column_key)
                    subject = Subject.objects.get(subject_name=class_card[key][column_key][row_key])
                    try:
                        teacher = class_normal.teacher.get(subject=subject)
                    except BaseException:
                        teacher = class_normal.head_master
                    card = Card(str(uuid.uuid1()).replace('-', ''), row.row_id, column.column_id, subject.subject_id, teacher.teacher_id, class_normal.class_id)
                    card.save()
    return JsonResponse({'status': 200})


def turn_out_card(request):
    grade_class = {}
    grade_teacher = {}
    for grade in Grade.objects.all():
        grade_class[grade.grade_name + '班级'] = []
        grade_teacher[grade.grade_name + '教师'] = []
        for class_normal in grade.classnormal_set.all():
            grade_class[grade.grade_name + '班级'].append(class_normal.class_name)
        for teacher in grade.teacher_set.all():
            grade_teacher[grade.grade_name + '教师'].append(teacher.teacher_name)
    row_cards = RowCard.objects.all().order_by('row_index')
    column_cards = ColumnCard.objects.all().order_by('column_index')
    return render(request, 'out_card.html', {'grade_class': grade_class,
                                             'grade_teacher': grade_teacher,
                                             'row_cards': row_cards,
                                             'column_cards': column_cards})


def get_class_card(request):
    class_name = request.POST.get('class_name')
    class_normal = ClassNormal.objects.get(class_name=class_name)
    items = []
    for class_card in class_normal.card_set.all():
        one_item = {'x': class_card.column.column_index,
                    'y': class_card.row.row_index,
                    'subject': class_card.subject.subject_name,
                    'teacher': class_card.teacher.teacher_name}
        items.append(one_item)
    return JsonResponse({'status': 200, 'item_cells': items})


def get_teacher_card(request):
    teacher_name = request.POST.get('teacher_name')
    teacher = Teacher.objects.get(teacher_name=teacher_name)
    items = []
    print(len(teacher.card_set.all()))
    for class_card in teacher.card_set.all():
        one_item = {'x': class_card.column.column_index,
                    'y': class_card.row.row_index,
                    'subject': class_card.subject.subject_name,
                    'class': class_card.class_normal.class_name}
        items.append(one_item)
    return JsonResponse({'status': 200, 'item_cells': items})


def change_class_card(request):
    data = json.loads(request.body.decode('utf-8'))
    class_name = data['class']
    from_card_dict = data['from']
    to_card_dict = data['to']
    if from_card_dict['subject'] == to_card_dict['subject']:
        return JsonResponse({'status': 200})

    class_normal = ClassNormal.objects.get(class_name=class_name)
    from_column = ColumnCard.objects.get(column_index=from_card_dict['column'])
    from_row = RowCard.objects.get(row_name=from_card_dict['row'])
    from_teacher = Teacher.objects.get(Q(teacher_name=from_card_dict['teacher']),
                                       Q(teacher_grade=class_normal.class_grade))
    from_subject = Subject.objects.get(subject_name=from_card_dict['subject'])

    to_column = ColumnCard.objects.get(column_index=to_card_dict['column'])
    to_row = RowCard.objects.get(row_name=to_card_dict['row'])
    to_teacher = Teacher.objects.get(Q(teacher_name=to_card_dict['teacher']),
                                       Q(teacher_grade=class_normal.class_grade))
    to_subject = Subject.objects.get(subject_name=to_card_dict['subject'])

    try:
        teacher_card = Card.objects.get(Q(row=from_row),
                                        Q(column=from_column),
                                        Q(teacher=to_teacher))
        return JsonResponse({'status': 300, 'teacher': to_teacher.teacher_name})
    except BaseException:
        pass

    try:
        teacher_card = Card.objects.get(Q(row=to_row),
                                        Q(column=to_column),
                                        Q(teacher=from_teacher))
        return JsonResponse({'status': 300, 'teacher': from_teacher.teacher_name})
    except BaseException:
        pass

    try:
        teacher_rule = TeacherRule.objects.get(Q(row_card=from_row),
                                               Q(column_card=from_column),
                                               Q(teacher=to_teacher))
        if teacher_rule.item == 1:
            return JsonResponse({'status': 303, 'teacher': to_teacher.teacher_name})
    except BaseException:
        pass

    try:
        teacher_rule = TeacherRule.objects.get(Q(row_card=to_row),
                                               Q(column_card=to_column),
                                               Q(teacher=from_teacher))
        if teacher_rule.item == 1:
            return JsonResponse({'status': 303, 'teacher': from_teacher.teacher_name})
    except BaseException:
        pass

    try:
        class_rule = class_normal.classnormalrule_set.get(Q(row_card=to_row),
                                                 Q(column_card=to_column))
        if class_rule.item != from_subject:
            return JsonResponse(
                {'status': 305, 'subject': class_rule.item})
    except BaseException:
        pass

    try:
        class_rule = class_normal.classnormalrule_set.get(Q(row_card=from_row),
                                                 Q(column_card=from_column))
        if class_rule.item != to_subject:
            return JsonResponse({'status': 305, 'subject': class_rule.item})
    except BaseException:
        pass

    from_card = Card.objects.get(Q(row=from_row),
                                 Q(column=from_column),
                                 Q(class_normal=class_normal))
    to_card = Card.objects.get(Q(row=to_row), Q(column=to_column),
                               Q(class_normal=class_normal))
    from_card.row = to_row
    from_card.column = to_column

    to_card.row = from_row
    to_card.column = from_column

    to_card.save()
    from_card.save()
    return JsonResponse({'status': 200})


