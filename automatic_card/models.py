from django.db import models

# Create your models here.


class Subject(models.Model):
    subject_id = models.CharField(primary_key=True, max_length=45)
    subject_name = models.CharField(max_length=20)
    class_normal = models.ManyToManyField(to='ClassNormal',
                                          through='SubjectClassNormal')
    teacher = models.ManyToManyField(to='Teacher')


class TeacherGroup(models.Model):
    group_id = models.CharField(primary_key=True, max_length=45)
    group_name = models.CharField(max_length=20)


class ClassType(models.Model):
    type_id = models.CharField(primary_key=True, max_length=45)
    type_name = models.CharField(max_length=20)


class Grade(models.Model):
    grade_id = models.CharField(primary_key=True, max_length=45)
    grade_name = models.CharField(max_length=10)
    class_type = models.ManyToManyField(to='ClassType')


class Teacher(models.Model):
    teacher_id = models.CharField(primary_key=True, max_length=45)
    teacher_name = models.CharField(max_length=10)
    teacher_group = models.ForeignKey(to='TeacherGroup',
                                         on_delete=models.CASCADE)
    teacher_grade = models.ForeignKey(to='Grade', on_delete=models.CASCADE)


# class SubjectTeacher(models.Model):
#     subject = models.ForeignKey(to='Subject', on_delete=models.CASCADE)
#     teacher = models.ForeignKey(to='Teacher', on_delete=models.CASCADE)
#     subject_number = models.IntegerField(blank=False, null=False)


class SubjectClassNormal(models.Model):
    subject = models.ForeignKey(to='Subject', on_delete=models.CASCADE)
    class_normal = models.ForeignKey(to='ClassNormal', on_delete=models.CASCADE)
    subject_number = models.IntegerField(blank=False, null=False)


class ClassNormal(models.Model):
    class_id = models.CharField(primary_key=True, max_length=45)
    class_name = models.CharField(max_length=45, null=False)
    class_type = models.ForeignKey(to=ClassType, on_delete=models.CASCADE)
    class_grade = models.ForeignKey(to=Grade, on_delete=models.CASCADE)
    teacher = models.ManyToManyField(to='Teacher')
    head_master = models.OneToOneField(to=Teacher, related_name='head_master_id'
                                       , null=True,
                                       on_delete=models.CASCADE)


class Semester(models.Model):
    semester_id = models.CharField(primary_key=True, max_length=45)
    semester_year = models.IntegerField(blank=False, null=False)
    semester_order = models.IntegerField(blank=False, null=False)


class RowCard(models.Model):
    row_id = models.CharField(primary_key=True, max_length=45)
    row_name = models.CharField(max_length=10)
    row_index = models.IntegerField(blank=False, null=False)
    section = models.CharField(max_length=10)
    semester = models.ForeignKey(to='Semester', on_delete=models.CASCADE)


class ColumnCard(models.Model):
    column_id = models.CharField(primary_key=True, max_length=45)
    column_name = models.CharField(max_length=10)
    column_index = models.IntegerField(blank=False, null=False)
    semester = models.ForeignKey(to='Semester', on_delete=models.CASCADE)


class Card(models.Model):
    card_id = models.CharField(primary_key=True, max_length=45)
    row = models.ForeignKey(to='RowCard', on_delete=models.CASCADE)
    column = models.ForeignKey(to='ColumnCard', on_delete=models.CASCADE)
    subject = models.ForeignKey(to='Subject', on_delete=models.CASCADE)
    teacher = models.ForeignKey(to='Teacher', on_delete=models.CASCADE, null=True, blank=True)
    class_normal = models.ForeignKey(to='ClassNormal', on_delete=models.CASCADE)


class TeacherRule(models.Model):
    rule_id = models.CharField(primary_key=True, max_length=45)
    row_card = models.ForeignKey(to='RowCard', on_delete=models.CASCADE)
    column_card = models.ForeignKey(to='ColumnCard', on_delete=models.CASCADE)
    item = models.CharField(max_length=10)
    teacher = models.ManyToManyField(to='Teacher')


class ClassNormalRule(models.Model):
    rule_id = models.CharField(primary_key=True, max_length=45)
    row_card = models.ForeignKey(to='RowCard', on_delete=models.CASCADE)
    column_card = models.ForeignKey(to='ColumnCard', on_delete=models.CASCADE)
    item = models.CharField(max_length=10)
    class_normal = models.ManyToManyField(to='ClassNormal')


class GradeRule(models.Model):
    rule_id = models.CharField(primary_key=True, max_length=45)
    row_card = models.ForeignKey(to='RowCard', on_delete=models.CASCADE)
    column_card = models.ForeignKey(to='ColumnCard', on_delete=models.CASCADE)
    item = models.CharField(max_length=10)
    grade = models.ManyToManyField(to='Grade')


class GradeSubject(models.Model):
    subject = models.ForeignKey(to='Subject', on_delete=models.CASCADE)
    grade = models.ForeignKey(to='Grade', on_delete=models.CASCADE)
    subject_number = models.IntegerField(blank=False, null=False)