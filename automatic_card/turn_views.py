from django.shortcuts import render
from automatic_card.models import *


def home(request):
    # grade1 = Grade(str(uuid.uuid1()).replace('-', ''), '高一')
    # grade2 = Grade(str(uuid.uuid1()).replace('-', ''), '高二')
    # grade3 = Grade(str(uuid.uuid1()).replace('-', ''), '高三')
    # grade4 = Grade(str(uuid.uuid1()).replace('-', ''), '补习班')
    # grade1.save()
    # grade2.save()
    # grade3.save()
    # grade4.save()
    # teacher_group1 = TeacherGroup(str(uuid.uuid1()).replace('-', ''), '领导')
    # teacher_group2 = TeacherGroup(str(uuid.uuid1()).replace('-', ''), '普通教师')
    # teacher_group1.save()
    # teacher_group2.save()
    # class_type1 = ClassType(str(uuid.uuid1()).replace('-', ''), '音乐班')
    # class_type2 = ClassType(str(uuid.uuid1()).replace('-', ''), '体育班')
    # class_type3 = ClassType(str(uuid.uuid1()).replace('-', ''), '混合班')
    # class_type1.save()
    # class_type2.save()
    # class_type3.save()
    # grades = Grade.objects.all()
    # class_types = ClassType.objects.all()
    # for grade in grades:
    #     for class_type in class_types:
    #         grade.class_type.add(class_type)
    return render(request, "home.html")


def start_input(request):
    return render(request, "tableInfo/table_info.html")


def turn_subject(request):
    subjects = Subject.objects.all()
    return render(request, 'subjectInfo/subject_info.html',
                  {'subjects': subjects})


def turn_teacher(request):
    grades = Grade.objects.all()
    teacher_groups = TeacherGroup.objects.all()
    teachers = Teacher.objects.all()
    subject_items = Subject.objects.all()
    has_teacher = True
    items = []
    if len(teachers) > 0:
        for teacher in teachers:
            subject_str = ''
            subjects = teacher.subject_set.all()
            subject_lenght = len(subjects)
            for i in range(subject_lenght):
                if i == subject_lenght - 1:
                    subject_str += subjects[i].subject_name
                else:
                    subject_str += subjects[i].subject_name + '、'
            one_item = {'teacher_name': teacher.teacher_name,
                        'subject': subject_str,
                        'group': teacher.teacher_group.group_name,
                        'grade': teacher.teacher_grade.grade_name}
            items.append(one_item)
    else:
        has_teacher = False
    return render(request, 'teacherInfo/teacher_info.html',
                  {'grades': grades,'groups': teacher_groups,
                   'has_teacher': has_teacher, 'items': items,
                   'subjects': subject_items})


def turn_class(request):
    class_normals = ClassNormal.objects.all()
    has_class = True
    grades = Grade.objects.all()
    class_types = ClassType.objects.all()
    if len(class_normals) == 0:
        has_class = False
    return render(request, 'classInfo/add_class.html',
                  {'class_normals': class_normals, 'has_class': has_class,
                   'grades': grades, 'class_types': class_types})


def turn_class_hour(request):
    subjects = Subject.objects.all()
    grade = Grade.objects.all()
    items = {}
    for one_grade in grade:
        class_types = []
        for one_class_type in one_grade.class_type.all():
            class_types.append(one_class_type.type_name)
        items[one_grade.grade_name] = class_types
    return render(request, 'classInfo/add_class_hour.html',
                  {'subjects': subjects, 'items': items})


def turn_class_edit(request):
    grades = Grade.objects.all()
    items = []
    for grade in grades:
        for class_type in grade.class_type.all():
            class_normals = class_type.classnormal_set.filter(class_grade=grade)
            for class_normal in class_normals:
                subject_hours = class_normal.subjectclassnormal_set.all()
                subject_hour_lenght = len(subject_hours)
                subject_hour = ''
                has_headmaster = True
                if not class_normal.head_master_id:
                    has_headmaster = False
                for i in range(subject_hour_lenght):
                    if i == subject_hour_lenght - 1:
                        subject_hour += subject_hours[i].subject.subject_name\
                                        + str(subject_hours[i].subject_number)\
                                        + '节'
                    else:
                        subject_hour += subject_hours[i].subject.subject_name\
                                        + str(subject_hours[i].subject_number)\
                                        + '节' + '、'
                if has_headmaster:
                    one_item = {'grade': grade.grade_name,
                                'class_type': class_type.type_name,
                                'class_name': class_normal.class_name,
                                'has_headmaster': has_headmaster,
                                'headmaster':
                                    class_normal.head_master.teacher_name,
                                'subject_hour': subject_hour
                                }
                else:
                    one_item = {'grade': grade.grade_name,
                                'class_type': class_type.type_name,
                                'class_name': class_normal.class_name,
                                'has_headmaster': has_headmaster,
                                'subject_hour': subject_hour
                                }
                items.append(one_item)
    class_types = ClassType.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'classInfo/edit_class.html',
                  {'items': items, 'grades': grades,
                   'class_types': class_types, 'subjects': subjects})


def turn_teacher_rule(request):
    groups = TeacherGroup.objects.all()
    row_cards = RowCard.objects.all().order_by('row_index')
    column_cards = ColumnCard.objects.all().order_by('column_index')
    return render(request, 'rule/teacher_rule.html',
                  {'groups': groups, 'row_cards': row_cards,
                   'column_cards': column_cards})


def turn_class_rule(request):
    subjects = Subject.objects.all()
    grade = Grade.objects.all()
    items = {}
    for one_grade in grade:
        class_types = []
        for one_class_type in one_grade.class_type.all():
            class_types.append(one_class_type.type_name)
        items[one_grade.grade_name] = class_types
    row_cards = RowCard.objects.all().order_by('row_index')
    column_cards = ColumnCard.objects.all().order_by('column_index')
    return render(request, 'rule/class_rule.html',
                  {'subjects': subjects, 'items': items, 'row_cards': row_cards,
                   'column_cards': column_cards})


def turn_make_card(request):
    return render(request, 'make_card.html')
