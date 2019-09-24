from django.shortcuts import render
from automatic_card.models import *
import uuid


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
    # subject1 = Subject(str(uuid.uuid1()).replace('-', ''), '语文')
    # subject2 = Subject(str(uuid.uuid1()).replace('-', ''), '数学')
    # subject3 = Subject(str(uuid.uuid1()).replace('-', ''), '英语')
    # subject4 = Subject(str(uuid.uuid1()).replace('-', ''), '历史')
    # subject5 = Subject(str(uuid.uuid1()).replace('-', ''), '政治')
    # subject6 = Subject(str(uuid.uuid1()).replace('-', ''), '地理')
    # subject7 = Subject(str(uuid.uuid1()).replace('-', ''), '专业')
    # subject8 = Subject(str(uuid.uuid1()).replace('-', ''), '扫除')
    # subject9 = Subject(str(uuid.uuid1()).replace('-', ''), '自习')
    # subject0 = Subject(str(uuid.uuid1()).replace('-', ''), '体育')
    # subject0.save()
    # subject1.save()
    # subject2.save()
    # subject3.save()
    # subject4.save()
    # subject5.save()
    # subject6.save()
    # subject7.save()
    # subject8.save()
    # subject9.save()
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
    class_type = ClassType.objects.all()
    grade = Grade.objects.all()
    return render(request, 'classInfo/add_class_hour.html',
                  {'subjects': subjects, 'class_type': class_type,
                   'grade': grade})


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
                for i in range(subject_hour_lenght):
                    if i == subject_hour_lenght - 1:
                        subject_hour += subject_hours[i].subject.subject_name\
                                        + str(subject_hours[i].subject_number)\
                                        + '节'
                    else:
                        subject_hour += subject_hours[i].subject.subject_name\
                                        + str(subject_hours[i].subject_number)\
                                        + '节' + '、'
                one_item = {'grade': grade.grade_name,
                            'class_type': class_type.type_name,
                            'class_name': class_normal.class_name,
                            'subject_hour': subject_hour
                            }
                items.append(one_item)
    class_types = ClassType.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'classInfo/edit_class.html',
                  {'items': items, 'grades': grades,
                   'class_types': class_types, 'subjects': subjects})