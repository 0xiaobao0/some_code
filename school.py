from db import Db
import random

class Teacher():
    #初始化一个教师对象时，在数据库创建一个名为name的教师记录，并返回其教师id，教师对象储存该id,
    # 该过程封装在一个事务里，从而保证高并发安全
    def __init__(self, name):
        self.create_sql = 'insert into teacher (teacher_name) VALUES("{}")'.format(name)
        self.get_id_sql = 'select teacher_id from teacher order by teacher_id DESC limit 1'
        self.db = Db()
        self.class_list = []
        self.id = None
        self.waiting_grade_homework_title = []
        self.waiting_grade_homework = []
        with self.db.connection.cursor() as cursor:
            try:
                cursor.execute(self.create_sql)
                cursor.execute(self.get_id_sql)
                res = cursor.fetchall()
                # print(res)
                self.id = res[0]['teacher_id']
                # print(self.id)
                self.db.connection.commit()

            except Exception as e:
                print(e)
                self.db.connection.rollback()

    #获取教师所在班级
    def get_class(self):
        with self.db.connection.cursor() as cursor:
            try:
                sql = 'select class_id from class where teacher_id={}'.format(self.id)
                cursor.execute(sql)
                res = cursor.fetchall()
                self.db.connection.commit()
                self.class_list = [i['class_id'] for i in res]
                print('教师{}所教授的班级为:'.format(self.id), self.class_list)
            except Exception as e:
                print('查询教师所教授的班级列表失败:', e)

    #获取教师所教授的某个班的所有学生
    def get_class_student(self, class_id):
        student_list = []
        with self.db.connection.cursor() as cursor:
            try:
                sql = 'select student_id from class_student where class_id={}'.format(class_id)
                cursor.execute(sql)
                res = cursor.fetchall()
                self.db.connection.commit()
                student_list += [j['student_id'] for j in res]
                print('查询教师{}所教授的{}班的所有学生成功:{}'.format(self.id, class_id, student_list))
            except Exception as e:
                print('查询教师所教授的{}班的学生失败'.format(class_id))
        return student_list

    #教师给其所教授的所有学生布置作业
    def set_homework(self, homework_title):
        self.get_class()
        with self.db.connection.cursor() as cursor:
            try:
                for i in self.class_list:
                    student_list = self.get_class_student(i)
                    for j in student_list:
                        sql = 'insert into homework (homework_title, student_id, class_id) VALUES ("{}", {}, {})'.format(
                            homework_title, j, i)
                        cursor.execute(sql)
                self.db.connection.commit()
                self.waiting_grade_homework_title.append(homework_title)
                print('教师{}布置作业完成'.format(self.id))
            except Exception as e:
                print('教师{}布置作业过程中出现意外'.format(self.id), e)
                self.db.connection.rollback()

    #教师获取其所布置所有成绩为空的作业
    def get_none_grade_homework(self, homework_title_list):
        # print(homework_title_list)
        with self.db.connection.cursor() as cursor:
            try:
                for i in homework_title_list:
                    sql = 'select homework_id, homework_content from homework where homework_title="{}" and grade is null'.format(i)
                    cursor.execute(sql)
                    res = cursor.fetchall()
                    self.waiting_grade_homework += res
                    self.waiting_grade_homework_title.pop(self.waiting_grade_homework_title.index(i))
                self.db.connection.commit()
                print('教师{}收作业成功'.format(self.id))
            except Exception as e:
                print('教师{}收作业失败', e)

    #教师给一个作业评分
    def set_score(self, homework, grade):
        homework_id = homework['homework_id']
        # print(homework_id)
        with self.db.connection.cursor() as cursor:
            try:
                sql = 'update homework set grade={} where homework_id={}'.format(grade, homework_id)
                cursor.execute(sql)
                self.db.connection.commit()
                self.waiting_grade_homework = list(filter(lambda x: x != homework, self.waiting_grade_homework))
                # index = self.waiting_grade_homework.index(homework)
                # self.waiting_grade_homework.pop(index)
                print('教师{}批改作业{}成功'.format(self.id, homework_id))
            except Exception as e:
                print('教师{}批改作业{}失败'.format(self.id, homework_id), e)
                self.db.connection.rollback()


class Student():
    #初始化一个学生对象时，在数据库创建一个名为name的学生记录，并返回其学生id，教师对象储存该id,
    # 该过程封装在一个事务里，从而保证高并发安全
    def __init__(self, name):
        self.create_sql = 'insert into student (student_name) VALUES("{}")'.format(name)
        self.get_id_sql = 'select student_id from student order by student_id DESC limit 1'
        self.db = Db()
        self.id = None
        self.homework_list = []
        with self.db.connection.cursor() as cursor:
            try:
                cursor.execute(self.create_sql)
                cursor.execute(self.get_id_sql)
                res = cursor.fetchall()
                # print(res)
                self.id = res[0]['student_id']
                # print(self.id)
                self.db.connection.commit()
            except Exception as e:
                print(e)
                self.db.connection.rollback()

    #学生获取作业
    def get_homework(self):
        with self.db.connection.cursor() as cursor:
            try:
                sql = 'select homework_id,homework_title from homework where student_id={} and grade is null'.format(self.id)
                cursor.execute(sql)
                res = cursor.fetchall()
                self.db.connection.commit()
                self.homework_list += res
                print('学生{}获取作业成功'.format(self.id))
            except Exception as e:
                print('学生{}获取作业失败'.format(self.id), e)

    #学生交作业
    def upload_home(self, homework_id, content):
        with self.db.connection.cursor() as cursor:
            try:
                sql = 'update homework set homework_content="{}" where homework_id={}'.format(content, homework_id)
                cursor.execute(sql)
                self.db.connection.commit()
                print('学生{}交作业成功'.format(self.id))
            except Exception as e:
                print('学生{}交作业失败'.format(self.id), e)
                self.db.connection.rollback()


class Course():
    # 初始化一个课程对象时，在数据库创建一个名为name的课程记录，并返回其课程id，课程对象储存该id,
    # 该过程封装在一个事务里，从而保证高并发安全
    def __init__(self, course_name, teacher_id):
        self.create_sql = 'insert into class (class_name, teacher_id) VALUES("{}", {})'.format(course_name, teacher_id)
        self.get_id_sql = 'select class_id from class order by class_id DESC limit 1'
        self.db = Db()
        self.id = None
        with self.db.connection.cursor() as cursor:
            try:
                cursor.execute(self.create_sql)
                cursor.execute(self.get_id_sql)
                res = cursor.fetchall()
                # print(res)
                self.id = res[0]['class_id']
                # print(self.id)
                self.db.connection.commit()
            except Exception as e:
                print(e)
                self.db.connection.rollback()

    #将学生添加到班级里
    def add_student(self, student_id):
        with self.db.connection.cursor() as cursor:
            try:
                sql = 'insert into class_student (class_id, student_id) values ({}, {})'.format(self.id, student_id)
                cursor.execute(sql)
                self.db.connection.commit()
            except Exception as e:
                print('班级{}加入学生{}失败'.format(self.id, student_id), e)
                self.db.connection.rollback()

#以下的逻辑为：有数学老师和语文老师两个老师，数学老师教授数学1班和2班，语文老师教授语文1班和2班，
# 编号1-10的学生在数学1班和语文1班上课，编号11-20的学生在数学2班和语文2班上课
student_list = []

math_teacher = Teacher('数学教师')
chinese_teacher = Teacher('语文教师')

class_1 = Course('数学班级1', math_teacher.id)
class_2 = Course('数学班级2', math_teacher.id)
class_3 = Course('语文班级1', chinese_teacher.id)
class_4 = Course('语文班级2', chinese_teacher.id)

for i in range(1, 21):
    if 1 <= i <= 10:
        student = Student('学生{}'.format(i))
        student_list.append(student)
        class_1.add_student(student.id)
        class_3.add_student(student.id)
    if 11 <= i <= 20:
        student = Student('学生{}'.format(i))
        student_list.append(student)
        class_2.add_student(student.id)
        class_4.add_student(student.id)


#语文老师和数学老师分别布置作业
chinese_teacher.set_homework('阅读理解')
math_teacher.set_homework('三角函数')

#学生获取作业
for student in student_list:
    student.get_homework()
    print(student.homework_list)
    for homework in student.homework_list:
        student.upload_home(homework['homework_id'], '学生{}完成的{}'.format(student.id, homework['homework_title']))

math_teacher.get_none_grade_homework(math_teacher.waiting_grade_homework_title)
print('教师{}待给分的作业有:'.format(math_teacher.id), math_teacher.waiting_grade_homework)
for homework in math_teacher.waiting_grade_homework:
    math_teacher.set_score(homework, random.randint(1, 5))
print('教师{}待给分的作业有:'.format(math_teacher.id), math_teacher.waiting_grade_homework)

chinese_teacher.get_none_grade_homework(chinese_teacher.waiting_grade_homework_title)
print('教师{}待给分的作业有:'.format(chinese_teacher.id), chinese_teacher.waiting_grade_homework)
for homework in chinese_teacher.waiting_grade_homework:
    chinese_teacher.set_score(homework, random.randint(1, 5))
print('教师{}待给分的作业有:'.format(chinese_teacher.id), chinese_teacher.waiting_grade_homework)

#关闭数据库连接对象
Db().connection.close()