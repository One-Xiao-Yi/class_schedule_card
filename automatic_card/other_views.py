from automatic_card.models import *
from django.http import JsonResponse
import json
import uuid
from xlwt import *
from io import BytesIO
from django.http import HttpResponse
from django.utils.http import urlquote
from django.db.models import Q


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
    Semester.objects.all().delete()
    RowCard.objects.all().delete()
    ColumnCard.objects.all().delete()
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


def export_one_class_card(request):
    class_name = request.GET.get('name')
    class_normal = ClassNormal.objects.get(class_name=class_name)
    cards = class_normal.card_set.all()
    card_dict = {}
    for card in cards:
        card_dict[str(card.row.row_index) + str(card.column.column_index)] = \
            card.subject.subject_name + ':' + card.teacher.teacher_name
    rows = RowCard.objects.all().order_by("row_index")
    columns = ColumnCard.objects.all().order_by("column_index")
    card_table = [['' for i in range(len(columns) + 1)]
                  for j in range(len(rows) + 1)]
    for column in columns:
        card_table[0][column.column_index] = column.column_name
    for row in rows:
        card_table[row.row_index + 1][0] = row.row_name
    for i in range(len(card_table)):
        for j in range(len(card_table[i])):
            if str(i - 1) + str(j) in card_dict:
                card_table[i][j] = card_dict[str(i - 1) + str(j)]
    ws = Workbook(encoding='utf-8')
    w = ws.add_sheet(class_name)
    for i in range(len(card_table)):
        for j in range(len(card_table[i])):
            w.write(i, j, card_table[i][j])
    sio = BytesIO()
    ws.save(sio)
    sio.seek(0)
    response = HttpResponse(sio.getvalue(),
                            content_type="application/vnd.ms-excel")
    response[
        'Content-Disposition'] = 'attachment; filename=' \
                                 + (urlquote(class_name)) + '.xls'  # 文件名
    response.write(sio.getvalue())
    return response


def export_one_teacher_card(request):
    name_grade = request.GET.get('name')
    grade = Grade.objects.get(grade_name=name_grade.split('|')[0]
                              .replace('教师', ''))
    teacher = Teacher.objects.get(Q(teacher_grade=grade),
                                  Q(teacher_name=name_grade.split('|')[1]))
    cards = teacher.card_set.all()
    card_dict = {}
    for card in cards:
        card_dict[str(card.row.row_index) + str(card.column.column_index)] = \
            card.subject.subject_name + ':' + card.teacher.teacher_name
    rows = RowCard.objects.all().order_by("row_index")
    columns = ColumnCard.objects.all().order_by("column_index")
    card_table = [['' for i in range(len(columns) + 1)]
                  for j in range(len(rows) + 1)]
    for column in columns:
        card_table[0][column.column_index] = column.column_name
    for row in rows:
        card_table[row.row_index + 1][0] = row.row_name
    for i in range(len(card_table)):
        for j in range(len(card_table[i])):
            if str(i - 1) + str(j) in card_dict:
                card_table[i][j] = card_dict[str(i - 1) + str(j)]
    ws = Workbook(encoding='utf-8')
    w = ws.add_sheet(teacher.teacher_name)
    for i in range(len(card_table)):
        for j in range(len(card_table[i])):
            w.write(i, j, card_table[i][j])
    sio = BytesIO()
    ws.save(sio)
    sio.seek(0)
    response = HttpResponse(sio.getvalue(),
                            content_type="application/vnd.ms-excel")
    response[
        'Content-Disposition'] = 'attachment; filename=' \
                                 + (urlquote(teacher.teacher_name)) + '.xls'  # 文件名
    response.write(sio.getvalue())
    return response


def export_all_class_card(request):
    ws = Workbook(encoding='utf-8')
    for grade in Grade.objects.all():
        for class_normal in grade.classnormal_set.all():
            cards = class_normal.card_set.all()
            card_dict = {}
            for card in cards:
                card_dict[
                    str(card.row.row_index) + str(card.column.column_index)] = \
                    card.subject.subject_name + ':' + card.teacher.teacher_name
            rows = RowCard.objects.all().order_by("row_index")
            columns = ColumnCard.objects.all().order_by("column_index")
            card_table = [['' for i in range(len(columns) + 1)]
                          for j in range(len(rows) + 1)]
            for column in columns:
                card_table[0][column.column_index] = column.column_name
            for row in rows:
                card_table[row.row_index + 1][0] = row.row_name
            for i in range(len(card_table)):
                for j in range(len(card_table[i])):
                    if str(i - 1) + str(j) in card_dict:
                        card_table[i][j] = card_dict[str(i - 1) + str(j)]
            w = ws.add_sheet(class_normal.class_name)
            for i in range(len(card_table)):
                for j in range(len(card_table[i])):
                    w.write(i, j, card_table[i][j])
    sio = BytesIO()
    ws.save(sio)
    sio.seek(0)
    response = HttpResponse(sio.getvalue(),
                            content_type="application/vnd.ms-excel")
    response[
        'Content-Disposition'] = 'attachment; filename=' \
                                 + (urlquote('班级课程表')) + '.xls'  # 文件名
    response.write(sio.getvalue())
    return response


def export_all_teacher_card(request):
    ws = Workbook(encoding='utf-8')
    for grade in Grade.objects.all():
        for teacher in grade.teacher_set.all():
            cards = teacher.card_set.all()
            card_dict = {}
            for card in cards:
                card_dict[
                    str(card.row.row_index) + str(card.column.column_index)] = \
                    card.subject.subject_name + ':' + card.teacher.teacher_name
            rows = RowCard.objects.all().order_by("row_index")
            columns = ColumnCard.objects.all().order_by("column_index")
            card_table = [['' for i in range(len(columns) + 1)]
                          for j in range(len(rows) + 1)]
            for column in columns:
                card_table[0][column.column_index] = column.column_name
            for row in rows:
                card_table[row.row_index + 1][0] = row.row_name
            for i in range(len(card_table)):
                for j in range(len(card_table[i])):
                    if str(i - 1) + str(j) in card_dict:
                        card_table[i][j] = card_dict[str(i - 1) + str(j)]
            w = ws.add_sheet(grade.grade_name + teacher.teacher_name)
            for i in range(len(card_table)):
                for j in range(len(card_table[i])):
                    w.write(i, j, card_table[i][j])
    sio = BytesIO()
    ws.save(sio)
    sio.seek(0)
    response = HttpResponse(sio.getvalue(),
                            content_type="application/vnd.ms-excel")
    response[
        'Content-Disposition'] = 'attachment; filename=' \
                                 + (urlquote('教师课程表')) + '.xls'  # 文件名
    response.write(sio.getvalue())
    return response
