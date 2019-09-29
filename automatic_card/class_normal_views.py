from automatic_card.models import *
from django.http import JsonResponse
import json
import uuid
from django.db.models import Q


def receive_class_type_info(request):
    data = request.POST.get('class_type_name')
    grade = Grade.objects.get(grade_name=request.POST.get('grade'))
    try:
        class_type = ClassType.objects.get(type_name=data)
        return JsonResponse({'status': 300})
    except BaseException:
        class_type = ClassType(str(uuid.uuid1()).replace('-', ''), data)
        class_type.save()
        grade.class_type.add(class_type)
        return JsonResponse({'status': 200})


def receive_class_info(request):
    data = json.loads(request.body.decode('utf-8'))
    grade = Grade.objects.get(grade_name=data['grade'])
    class_type = ClassType.objects.get(type_name=data['class_type'])
    has_class_normals_len = len(ClassNormal.objects.filter(class_grade=grade)
                                .filter(class_type=class_type))
    for i in range(int(data['class_number'])):
        class_normal = ClassNormal(str(uuid.uuid1()).replace('-', ''),
                                   grade.grade_name + class_type.type_name
                                   + str(i + has_class_normals_len + 1) + '班',
                                   class_type.type_id,grade.grade_id)
        class_normal.save()
    return JsonResponse({'status': 200,
                         'has_class_number': has_class_normals_len})


def receive_subject_hour_info(request):
    data = json.loads(request.body.decode('utf-8'))
    item_name = data['class_name']
    items = item_name.split('|')
    subject_hours = data['subject_hours']
    all_subject_number = 0
    for subject_hour in subject_hours:
        if not subject_hour['number'] == '':
            all_subject_number += int(subject_hour['number'])
    to_subject_number = len(RowCard.objects.all()) * len(
                ColumnCard.objects.all())
    grade = Grade.objects.get(grade_name=items[0])
    if len(items) == 1:
        if all_subject_number > to_subject_number:
            return JsonResponse({'status': 300, 'now': all_subject_number,
                                 'to': to_subject_number})
        class_normals = grade.classnormal_set.all()
        for subject_hour in subject_hours:
            subject = Subject.objects.get(
                subject_name=subject_hour['subject_name'])
            if not subject_hour['number'] or subject_hour['number'] == '':
                try:
                    grade_subject = GradeSubject.objects.get(Q(grade=grade),
                                                             Q(subject=subject))
                    grade_subject.delete()
                except BaseException:
                    continue
            else:
                try:
                    grade_subject = GradeSubject.objects.get(Q(grade=grade),
                                                             Q(subject=subject))
                    grade_subject.subject_number = subject_hour['number']
                    grade_subject.save()
                except BaseException:
                    grade_subject = GradeSubject(grade_id=grade.grade_id,
                                                 subject_id=subject.subject_id,
                                                 subject_number=
                                                 subject_hour['number'])
                    grade_subject.save()
    else:
        if not all_subject_number == to_subject_number:
            return JsonResponse({'status': 300, 'now': all_subject_number,
                                 'to': to_subject_number})
        class_type = grade.class_type.get(type_name=items[1])
        class_normals = ClassNormal.objects.filter(class_grade=grade)\
            .filter(class_type=class_type)
    for subject_hour in subject_hours:
        subject = Subject.objects.get(
            subject_name=subject_hour['subject_name'])
        if not subject_hour['number'] or subject_hour['number'] == '':
            for class_normal in class_normals:
                try:
                    subject_class_normal = SubjectClassNormal.objects.get(
                        Q(subject=subject), Q(class_normal=class_normal))
                    subject_class_normal.delete()
                except BaseException:
                    continue
        else:
            for class_normal in class_normals:
                try:
                    subject_class_normal = SubjectClassNormal.objects.get(
                        Q(subject=subject), Q(class_normal=class_normal))
                    subject_class_normal.subject_number = subject_hour['number']
                    subject_class_normal.save()
                except BaseException:
                    subject_class_normal = SubjectClassNormal(
                        subject_id=subject.subject_id,
                        class_normal_id=class_normal.class_id,
                        subject_number=int(subject_hour['number']))
                    subject_class_normal.save()
    return JsonResponse({'status': 200})


def get_class_hour(request):
    grade_type = request.POST.get('grade_type').split('|')
    grade = Grade.objects.get(grade_name=grade_type[0])
    items = []
    if len(grade_type) == 1:
        for subject_class in grade.gradesubject_set.all():
            items.append({'subject_name': subject_class.subject.subject_name,
                          'number': subject_class.subject_number})
    else:
        class_type = grade.class_type.get(type_name=grade_type[1])
        class_normal = ClassNormal.objects.filter(class_grade=grade)\
            .filter(class_type=class_type)[0]
        for subject_class in class_normal.subjectclassnormal_set.all():
            items.append({'subject_name': subject_class.subject.subject_name,
                          'number': subject_class.subject_number})
    return JsonResponse({'items': items})


def delete_class_normal(request):
    data = request.POST.get('class_name')
    class_normal = ClassNormal.objects.get(class_name=data)
    class_normal.delete()
    return JsonResponse({'status': 200})


def update_class_normal(request):
    data = json.loads(request.body.decode('utf-8'))
    class_name = data['class_name']
    class_normal = ClassNormal.objects.get(class_name=class_name)
    subjects = data['subjects']
    receive_subject_hour = {}
    get_subject_hour = {}
    for receive_subject_number in subjects:
        if not receive_subject_number['number'] == '':
            receive_subject_hour[receive_subject_number['subject_name']] = \
                receive_subject_number['number']
    for get_subject_number in class_normal.subjectclassnormal_set.all():
        get_subject_hour[get_subject_number.subject.subject_name] = \
            get_subject_number.subject_number
    error_subject_name = []
    error_hour = []
    for key in receive_subject_hour.keys():
        if key in get_subject_hour:
            if int(receive_subject_hour[key]) > int(get_subject_hour[key]):
                error_hour.append({'subject_name': str(key)})
        else:
            error_subject_name.append({'subject_name': str(key)})
    if len(error_subject_name) > 0 or len(error_hour) > 0:
        return JsonResponse({'status': 300, 'high_hour': error_hour,
                             'no_subject': error_subject_name})
    for subject_name in subjects:
        if subject_name['number'] == '':
            continue
        elif int(subject_name['number']) == 0:
            subject = Subject.objects.get(subject_name=
                                          subject_name['subject_name'])
            subject_hour = SubjectClassNormal.objects.get(Q(subject=subject),
                                                          Q(class_normal=
                                                            class_normal))
            subject_hour.delete()
        else:
            subject = Subject.objects.get(subject_name=
                                          subject_name['subject_name'])
            try:

                subject_hour = SubjectClassNormal.objects.get(Q(subject=subject),
                                                          Q(class_normal=
                                                            class_normal))
                subject_hour.subject_number = subject_name['number']
                subject_hour.save()
            except BaseException:
                subject_class_normal = SubjectClassNormal(
                    subject_id=subject.subject_id,
                    class_normal_id=class_normal.class_id,
                    subject_number=int(subject_name['number']))
                subject_class_normal.save()
    class_normal.save()
    class_hour_str = ''
    class_hours = class_normal.subjectclassnormal_set.all()
    for i in range(len(class_hours)):
        if i == len(class_hours) - 1:
            class_hour_str += class_hours[i].subject.subject_name + \
                              str(class_hours[i].subject_number) + '节'
        else:
            class_hour_str += class_hours[i].subject.subject_name + \
                              str(class_hours[i].subject_number) + '节、'
    return JsonResponse({'status': 200, 'class_name': class_normal.class_name,
                         'class_hour': class_hour_str})


def get_grade_teacher_info(request):
    data = str(request.POST.get('class_name')).strip().replace('"', '')
    class_normal = ClassNormal.objects.get(class_name=data)
    grade = class_normal.class_grade
    teachers = Teacher.objects.filter(teacher_grade=grade)
    items = []
    for teacher in teachers:
        items.append(teacher.teacher_name)
    return JsonResponse({'teachers': items})


def receive_headmaster(request):
    data = json.loads(request.body.decode('utf-8'))
    class_normal = ClassNormal.objects.get(class_name=data['class_name'])
    teacher = Teacher.objects.get(Q(teacher_name=data['teacher']),
                                  Q(teacher_grade=class_normal.class_grade))
    class_normal.head_master = teacher
    class_normal.save()
    return JsonResponse({'status': 200})
