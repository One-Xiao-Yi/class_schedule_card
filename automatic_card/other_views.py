from automatic_card.models import *
from django.http import JsonResponse
import json
import uuid


def receive_table_info(request):
    data = json.loads(request.body.decode('utf-8'))
    year = int(data['year'])
    order = int(data['order'])
    days = int(data['days'])
    early = int(data['early'])
    morning = int(data['morning'])
    afternoon = int(data['afternoon'])
    night = int(data['night'])
    one_day = early + morning + afternoon + night
    row_numbers = []
    semester = Semester(str(uuid.uuid1()).replace('-', ''),
                        int('20' + str(year)), order)
    semester.save()
    switch = {
        0: '星期一',
        1: '星期二',
        2: '星期三',
        3: '星期四',
        4: '星期五',
        5: '星期六',
        6: '星期日'
    }
    for day in range(days):
        column = ColumnCard(str(uuid.uuid1()).replace('-', ''), switch[day],
                            day + 1, semester.semester_id)
        column.save()
        semester.columncard_set.add(column)
    for i in range(one_day):
        if i < early:
            section = 'early'
            row_name = '早读' + str(i + 1)
        elif i < morning + early:
            section = 'morning'
            row_name = str(i - early + 1)
        elif i < afternoon + morning + early:
            section = 'afternoon'
            row_name = str(i - early + 1)
        else:
            section = 'night'
            row_name = '晚读' + str(i - afternoon - morning - early + 1)
        row_number = RowCard(str(uuid.uuid1()).replace('-', ''),
                             row_name, i, section, semester.semester_id)
        row_numbers.append(row_number)
    for item in row_numbers:
        item.save()
        semester.rowcard_set.add(item)
    return JsonResponse({'status': 200})


def receive_subject_info(request):
    data = request.POST.get('subject_name')
    try:
        subject = Subject.objects.get(subject_name=data)
        return JsonResponse({'status': 300})
    except BaseException:
        subject_class = Subject(str(uuid.uuid1()).replace('-',''), data)
        subject_class.save()
        return JsonResponse({'status': 200})


def delete_subject(request):
    data = request.POST.get('subject_name')
    subject = Subject.objects.get(subject_name=data)
    subject.delete()
    return JsonResponse({'status': 200})