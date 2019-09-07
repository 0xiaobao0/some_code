import pymysql.cursors
import threading

#创建了一个多线程安全的单例数据库对象，
#数据库中含有学生表，老师表，班级表，班级学生表，作业表，共5张表，相关字段用外键关联

def synchronized(func):
    func.__lock__ = threading.Lock()

    def lock_func(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)
    return lock_func

class Db(object):
    isinstance = None
    flag = True

    @synchronized
    def __new__(cls, *args, **kwargs):
        if cls.isinstance == None:
            cls.isinstance = super().__new__(cls)
        return cls.isinstance

    def __init__(self):
        if not Db.flag:
            return
        Db.flag = False
        teacher_table = """
            CREATE TABLE IF NOT EXISTS `teacher`  (
            `teacher_id` int(8) NOT NULL AUTO_INCREMENT,
            `teacher_name` VARCHAR(10) NOT NULL,
            PRIMARY KEY (`teacher_id`) USING BTREE
            ) ENGINE = InnoDB CHARSET=utf8 COLLATE=utf8_general_ci ROW_FORMAT = Compact;
                """
        class_table = """
            CREATE TABLE IF NOT EXISTS `class`  (
            `class_id` int(8) NOT NULL AUTO_INCREMENT,
            `class_name` VARCHAR(6) NOT NULL ,
            `teacher_id` int(8) NOT NULL,
            PRIMARY KEY (`class_id`) USING BTREE,
            INDEX `teacher_id_c`(`teacher_id`) USING BTREE,
            CONSTRAINT `teacher_id_c` FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`teacher_id`) ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE = InnoDB CHARSET=utf8 COLLATE=utf8_general_ci ROW_FORMAT = Compact;
                """
        student_table = """
            CREATE TABLE IF NOT EXISTS `student`  (
            `student_id` int(8) NOT NULL AUTO_INCREMENT,
            `student_name` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
            PRIMARY KEY (`student_id`) USING BTREE
            ) ENGINE = InnoDB CHARSET=utf8 COLLATE=utf8_general_ci ROW_FORMAT = Compact;
            """
        homework_table = """
            CREATE TABLE IF NOT EXISTS `homework`  (
            `homework_id` int(8) NOT NULL AUTO_INCREMENT,
            `student_id` int(8) NOT NULL,
            `class_id` int(8) NOT NULL,
            `homework_title` VARCHAR(100),
            `homework_content` VARCHAR (10000),
            `grade` tinyint(2),
            PRIMARY KEY (`homework_id`) USING BTREE,
            INDEX `student_id_h`(`student_id`) USING BTREE,
            INDEX `class_id_h`(`class_id`) USING BTREE,
            CONSTRAINT `class_id_h` FOREIGN KEY (`class_id`) REFERENCES `class` (`class_id`) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT `student_id_h` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;
        """

        class_student = """
          CREATE TABLE `class_student`  (
          `id` int(8) NOT NULL AUTO_INCREMENT,
          `class_id` int(8) NOT NULL,
          `student_id` int(8) NOT NULL,
          PRIMARY KEY (`id`) USING BTREE,
          INDEX `class_id_cs`(`class_id`) USING BTREE,
          INDEX `student_id_cs`(`student_id`) USING BTREE,
          CONSTRAINT `class_id_cs` FOREIGN KEY (`class_id`) REFERENCES `class` (`class_id`) ON DELETE CASCADE ON UPDATE CASCADE,
          CONSTRAINT `student_id_cs` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE
          ) ENGINE = InnoDB CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Compact;
                  """
        try:
            self.connect_db()
            with self.connection.cursor() as cursor:
                cursor.execute(teacher_table)
                cursor.execute(class_table)
                cursor.execute(student_table)
                cursor.execute(homework_table)
                cursor.execute(class_student)
                self.connection.commit()
                # result = cursor.fetchone()
                # return
                print('sql excute success')

        except Exception as e:
            self.connection.rollback()
            print(e)


    def connect_db(self):
        # Connect to the database
        self.connection = pymysql.connect(host='localhost',
                                      user='root',
                                      password='123',
                                      db='test',
                                      charset='utf8',
                                      cursorclass=pymysql.cursors.DictCursor)

