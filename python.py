from ast import Return
from genericpath import exists
from importlib.resources import contents
from itertools import count
from sqlite3 import Cursor, connect
from tabnanny import check
from flask import Flask, render_template, request, flash, abort, current_app, make_response
from sqlalchemy import false, true
from werkzeug.utils import secure_filename
from gtts import gTTS
from flask import jsonify
import os
from playsound import playsound
import time
from os import path
import playsound
import webbrowser
import speech_recognition as sr
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import mysql.connector
connection = pymysql.connect(
    host="localhost", user="root", password="*Login*1", database="mydb")


cursor = connection.cursor()
connection.autocommit(True)


def speak(text):
    tts = gTTS(text=text, lang='ar', slow=False)
    filename = 'voice.mp3'
    tts.save(filename)
    playsound.playsound(filename)
    os.remove('voice.mp3')


app = Flask(__name__)
app.secret_key = "manbearpig_MUDMAN888"


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/ereg", methods=['POST'])
def ereg():
    std_id = request.form.get('x')
    return render_template("ereg.html", std_id=std_id)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/loginforstudent", methods=['POST'])
def loginforstudent():

    id = request.form.get("number")
    # print(id)
    password = request.form.get("password")

    q1 = "select std_info.password from std_info where std_info.std_id = (%s)"
    v1 = (id)
    cursor.execute(q1, v1)
    connection.commit()
    dd = cursor.fetchone()[0]
    result = check_password_hash(dd, password)

    value = request.form.getlist('check')
    b = int(id)
    if(value[0] == "notadmin"):
        q = ("SELECT count(*) FROM  std_info WHERE std_id=(%s)")
        v = (b)
        cursor.execute(q, v)
        value3 = cursor.fetchone()[0]
        if (value3 == 0):
            return render_template("login.html")
        else:
            if (result):

                q = ("SELECT * FROM  std_info WHERE std_id=(%s)")
                v = (b)
                cursor.execute(q, v)
                data = cursor.fetchall()
                return render_template("afterlogin.html", value=data)
            else:
                return render_template("login.html")
    else:
        return render_template("login.html")


@app.route("/StudentSchedule", methods=['POST'])
def StudentSchedule():
    std_id = request.form.get("y")
    q = (
        "select concat (section.full_building_name,' (',section.building,')'), CONCAT (section.building,'-' ,section.room_id) AS 'class_room',CONCAT( instructor_info.f_name ,' ', instructor_info.l_name  ) AS 'inst_name' , CONCAT ('[',section_time.start_time,' - ' ,section_time.end_time,'] ',section_time.day) AS 'time' , section.section_id,course.noOfHours,course.course_name,section.course_id from section join course on course.course_id = section.course_id join instructor_info on instructor_info.inst_id = section.inst_id join section_time on section_time.sec_time_id = section.section_time join registered_courses on (registered_courses.course_id=section.course_id and registered_courses.sec_id= section.section_id) where registered_courses.std_id=(%s)")
    v = (std_id)
    cursor.execute(q, v)
    data = cursor.fetchall()

    return render_template("StudentSchedule.html", value=data, v2=std_id)


@app.route("/chgpass", methods=['POST'])
def chgpass():
    std_id = request.form.get("x")
    return render_template("chgpass.html", v=std_id)


@app.route("/StudentInfo", methods=['POST'])
def StudentInfo():
    std_id = request.form.get("y")
    print(std_id)
    q = ("SELECT std_info.std_id ,CONCAT(std_info.f_name,' ',std_info.l_name)as name,std_info.gender,std_info.dept_name,std_info.phone_number,std_info.email from std_info where std_info.std_id=(%s)")
    v = (std_id)
    cursor.execute(q, v)
    data = cursor.fetchall()
    return render_template("StudentInfo.html", value=data, v2=std_id)


@app.route("/StudentRegistration", methods=['POST'])
def StudentRegistration():
    name = request.form.get("y")
    std_id = request.form.get("x")
    q = ("SELECT course.course_id,course.course_name,course.noOfHours,plan.req_type FROM  course JOIN plan  on course.course_id=plan.course_id and dept_name=(%s)")
    v = (name)
    cursor.execute(q, v)
    data2 = cursor.fetchall()
    return render_template("StudentRegistration.html", value=data2, v=name, v2=std_id)


@app.route("/speak_ajax", methods=['POST'])
def speak_ajax():
    text = request.form['name']
    speak(text)
    return "ok"


@app.route("/confirm_ajax", methods=['POST'])
def confirm_ajax():
    std_id = request.form['std_id']
    time.strftime("%H:%M:%S")
    currenttime = str(time.strftime("%H:%M:%S"))
    print(currenttime)
# Actual Start Time
    timetogo = "23:37:10"

# Time for testing (uncomment)
#timetogo = "18:00:00"

    while True:
        # print("start")
        currenttime = str(time.strftime("%H:%M:%S"))
        if currenttime == timetogo:
            print("hello")
            q = "select * from temp_registered_courses where temp_registered_courses.std_id = (%s)"
            v = (std_id)
            cursor.execute(q, v)
            section = cursor.fetchall()
            # print(section)

            for x in section:
                c = x[2]
                s = x[1]
                print(c)
                print(s)
                # q = "select classroom.room_capacity from classroom join section on (section.room_id = classroom.room_id and classroom.building = section.building) where  section.section_id =(%s) and section.course_id = (%s)"
                q = "select classroom.room_capacity from classroom join section on classroom.room_id = section.room_id where section.course_id = (%s) and section.section_id =(%s) "
                v = (c, s)
                cursor.execute(q, v)

                capacity = cursor.fetchone()[0]
                if capacity == 0:
                    return jsonify("الشعبة مغلقة")
                else:
                    q = "select std_info.financial_record from std_info where std_info.std_id = (%s)"
                    v = (std_id)
                    cursor.execute(q, v)
                    fr = cursor.fetchone()[0]
                    fr1 = fr

                    q = "select course.noOfHours from course where course.course_id = (%s)"
                    v = (c)
                    cursor.execute(q, v)

                    cp = cursor.fetchone()[0]

                    price = cp*24

                    fr1 = fr1-price

                    if (fr1 < 0):
                        return ("السجل المالي غير كافي")
                    else:
                        # q = ("UPDATE std_info SET phone_number=(%s),email=(%s) where std_id=(%s)")
                        print(capacity)
                        capacity = capacity-1

                        q = "update classroom join  section on classroom.room_id = section.room_id set classroom.room_capacity = (%s) where  section.section_id =(%s) and section.course_id = (%s) "
                        v = (capacity, s, c)
                        cursor.execute(q, v)

                        #                     INSERT INTO table_name (column1, column2, column3, ...)
                # VALUES (value1, value2, value3, ...);

                        q11 = "insert into registered_courses (std_id , course_id , sec_id) values (%s,%s,%s)"
                        v11 = (std_id, c, s)
                        cursor.execute(q11, v11)

                        q1 = "select std_info.hours from std_info where std_info.std_id=(%s) "
                        v1 = (std_id)
                        cursor.execute(q1, v1)
                        sh = cursor.fetchone()[0]
                        sh = sh + cp

                        q9 = (
                            "UPDATE std_info SET std_info.hours = (%s) WHERE std_info.std_id = (%s)")
                        v9 = (sh, std_id)
                        cursor.execute(q9, v9)

                        q10 = (
                            "UPDATE std_info SET std_info.financial_record = (%s) WHERE std_info.std_id = (%s)")
                        v10 = (fr1, std_id)
                        cursor.execute(q10, v10)

            return "ok"


@app.route("/temp_ajax", methods=['POST'])
def temp_ajax():
    std_id = request.form['std_id']
    course_id = request.form['course_id']
    s_id = request.form['s_id']

    q = "select count(*) from section where section.course_id = (%s) and section.section_id = (%s)"
    v = (course_id, s_id)
    cursor.execute(q, v)
    value = cursor.fetchone()[0]
    if (value == 0):
        q1 = "select count(*) from course where course.course_id = (%s)"
        v = (course_id)
        cursor.execute(q, v)
        value2 = cursor.fetchone()[0]
        if (value2 == 0):
            return jsonify("رقم المساق غير صحيح")
        else:
            return jsonify("رقم الشعبة غير صحيح")

    else:
        q = ("SELECT section.section_time from section where section.course_id=(%s) and section.section_id=(%s)")
        v = (course_id, s_id)
        cursor.execute(q, v)
    # section time id for course id
        curr_sec_time_id = cursor.fetchone()[0]
        # وقت الشعبة

# اذاا الطالب مسجل هاي المادة من قبل او لا
        q1 = ("select count(*) from temp_registered_courses where temp_registered_courses.course_id=(%s)  and temp_registered_courses.std_id=(%s)")
        v1 = (course_id,  std_id)
        cursor.execute(q1, v1)
        data2 = cursor.fetchone()[0]

        q3 = ("select section_time.sec_time_id from  section_time join section on section.section_time = section_time.sec_time_id join temp_registered_courses on section.section_id=temp_registered_courses.sec_id and section.course_id=temp_registered_courses.course_id where temp_registered_courses.std_id=(%s)")
        v3 = (std_id)
        cursor.execute(q3, v3)
        flag = true
# اذا الطالب مش مسجل ولا شعبة من هاي المادة بفوت ع هاي الاف
        if (data2 == 0):
            # جدول التعارض
            for row in cursor:
                if row[0] == curr_sec_time_id:
                    flag = false
                    break
                elif curr_sec_time_id == 1 or curr_sec_time_id == 2:
                    if(row[0] == 5 or row[0] == 10 or row[0] == 12):

                        flag = false
                        break

                elif curr_sec_time_id == 3 or curr_sec_time_id == 4:
                    if(row[0] == 6 or row[0] == 11 or row[0] == 13):

                        flag = false
                        break

                elif curr_sec_time_id == 7 or curr_sec_time_id == 8:
                    if(row[0] == 9 or row[0] == 14):

                        flag = false
                        break

                elif curr_sec_time_id == 5 or curr_sec_time_id == 10 or curr_sec_time_id == 12:
                    if(row[0] == 1 or row[0] == 2):

                        flag = false
                        break

                elif (curr_sec_time_id == 6 or curr_sec_time_id == 11 or curr_sec_time_id == 13):
                    if(row[0] == 3 or row[0] == 4):

                        flag = false
                        break

                elif curr_sec_time_id == 9 or curr_sec_time_id == 14:
                    if(row[0] == 7 or row[0] == 8):

                        flag = false
                        break

                # else:

                continue

                # الفلاج ترو يعني ما في تعارض
            if flag == true:

                # كل الامور تمام

                #                     INSERT INTO table_name (column1, column2, column3, ...)
                # VALUES (value1, value2, value3, ...);

                q7 = (
                    "insert into mydb.temp_registered_courses (std_id,course_id,sec_id) values (%s,%s,%s)")
                v7 = (std_id, course_id, s_id)
                cursor.execute(q7, v7)
                connection.commit()

                return jsonify(
                    "اكتملت العملية بنجاح"
                )

            else:

                return jsonify(
                    "هذا المساق يتعارض مع مساق اخر في نفس الوقت"
                )
        else:
            return jsonify(
                "انت بالفعل ملتحق بشعبة من هذا المساق يجب عليك حذف المساق ثم اعادة الالتحاق بشعبة اخرى"
            )


@app.route("/process_ajax", methods=['POST'])
def process_ajax():
    cl = request.form['cl']
    q = (
        "SELECT  DISTINCT section.course_id,section.section_id,CONCAT (section.building,'-' ,section.room_id) AS 'class_room',CONCAT ('[',section_time.start_time,' - ' ,section_time.end_time,'] ',section_time.day) AS 'time'    ,CONCAT( instructor_info.f_name ,' ', instructor_info.l_name  ) AS 'inst_name' , classroom.room_capacity FROM section JOIN classroom on section.room_id=classroom.room_id  join section_time on section.section_time= section_time.sec_time_id join  instructor_info on section.inst_id =instructor_info.inst_id  and  section.course_id=(%s)")
    v = (cl)
    cursor.execute(q, v)
    data = cursor.fetchall()

    section = []
    for result in data:
        contents = {'cap': result[5],
                    'r_id': result[4],
                    's_time': result[3],
                    'inst_name': result[2],
                    's_id': result[1],
                    }
        section.append(contents)

    return jsonify(section)


@app.route("/student_info_ajax", methods=['POST'])
def student_info_ajax():
    std_id = request.form['std_id']
    phone = request.form['phone']
    email = request.form['email']
    q = ("UPDATE std_info SET phone_number=(%s),email=(%s) where std_id=(%s)")
    v = (phone, email, std_id)
    cursor.execute(q, v)

    return jsonify(phone, email, "yes")


@app.route("/chgpass_ajax", methods=['POST'])
def chgpass_ajax():
    std_id = request.form['std_id']
    base = request.form['base']
    passOne = request.form['passOne']
    passTwo = request.form['passTwo']
    # print("eaffffffffffffffffffffffffffffffffffffffff")
    # print(std_id)
    # print(base)
    q = ("SELECT std_info.password from std_info where std_id=(%s)")
    v = (std_id)
    cursor.execute(q, v)
    data = cursor.fetchone()[0]
    # print(data)
    result = check_password_hash(data, base)

    if (result):
        password = generate_password_hash(passOne, method='sha256')
        q2 = ("UPDATE std_info SET password=(%s) where std_id=(%s)")
        v2 = (password, std_id)
        cursor.execute(q2, v2)
        return jsonify("yes")

    else:
        return jsonify("NO")


@app.route("/registration_ajax", methods=['POST'])
def registration_ajax():
    cl = request.form['cl']
    sl = request.form['sl']
    std_id = request.form['std_id']

    q = ("SELECT section.section_time from section where section.course_id=(%s) and section.section_id=(%s)")
    v = (cl, sl)
    cursor.execute(q, v)
    # section time id for course id
    curr_sec_time_id = cursor.fetchone()[0]

    q = ("SELECT count(*) from registered_courses where std_id=(%s) ")
    v = (std_id)
    cursor.execute(q, v)

    num = cursor.fetchone()[0]
    print(num)

    q = ("SELECT sum(course.noOfHours) from course join section on course.course_id=section.course_id join registered_courses on registered_courses.course_id = section.course_id  where  registered_courses.std_id=(%s) ")
    v = (std_id)
    cursor.execute(q, v)

    num1 = cursor.fetchone()[0]
    print(num1)


# and registered_courses.sec_id=(%s)
    q1 = ("select count(*) from registered_courses where registered_courses.course_id=(%s)  and registered_courses.std_id=(%s)")
    v1 = (cl,  std_id)
    cursor.execute(q1, v1)
    data2 = cursor.fetchone()[0]

    # q2 = ("select count(*) from registered_courses where registered_courses.course_id=(%s) and registered_courses.sec_id=(%s) and registered_courses.std_id=(%s)")
    # v2 = (cl, sl, std_id)
    # cursor.execute(q1, v1)
    # data2 = cursor.fetchone()[0]

    # q3 = ("select * from section_time where 'احد' LIKE CONCAT('%',day,'%')")
    # q3 = ("select * from section_time where  day like '%احد ثلاثاء خميس%' ")
    q3 = ("select section_time.sec_time_id from  section_time join section on section.section_time = section_time.sec_time_id join registered_courses on section.section_id=registered_courses.sec_id and section.course_id=registered_courses.course_id where registered_courses.std_id=(%s)")
    v3 = (std_id)
    cursor.execute(q3, v3)
    flag = true

    if (data2 == 0):

        for row in cursor:
            if row[0] == curr_sec_time_id:

                flag = false
                break
            elif curr_sec_time_id == 1 or curr_sec_time_id == 2:
                if(row[0] == 5 or row[0] == 10 or row[0] == 12):

                    flag = false
                    break

            elif curr_sec_time_id == 3 or curr_sec_time_id == 4:
                if(row[0] == 6 or row[0] == 11 or row[0] == 13):

                    flag = false
                    break

            elif curr_sec_time_id == 7 or curr_sec_time_id == 8:
                if(row[0] == 9 or row[0] == 14):

                    flag = false
                    break

            elif curr_sec_time_id == 5 or curr_sec_time_id == 10 or curr_sec_time_id == 12:
                if(row[0] == 1 or row[0] == 2):

                    flag = false
                    break

            elif (curr_sec_time_id == 6 or curr_sec_time_id == 11 or curr_sec_time_id == 13):
                if(row[0] == 3 or row[0] == 4):

                    flag = false
                    break

            elif curr_sec_time_id == 9 or curr_sec_time_id == 14:
                if(row[0] == 7 or row[0] == 8):

                    flag = false
                    break

            # else:

            continue
            # return jsonify("hiiiiiiiiiiiiiiiiiiiii")

        if flag == true:

            q4 = (
                "select std_info.financial_record from std_info where std_info.std_id=(%s)")
            v4 = (std_id)
            cursor.execute(q4, v4)
            fr = cursor.fetchone()[0]
            fr1 = fr

            q5 = ("select course.noOfHours from course where course.course_id=(%s)")
            v5 = (cl)
            cursor.execute(q5, v5)
            cp = cursor.fetchone()[0]
            print(cp)
            price = cp*24
            print(price)
            fr1 = fr1-price
            print(fr1)

            if fr1 >= 0:

                #q6 = ("select sum(course.noOfHours)  from course join section on course.course_id= section.course_id join registered_courses on (registered_courses.course_id=section.course_id) where registered_courses.std_id=(%s) group by course.course_id")
                #q6 = ("select distinct course.course_name,(course.noOfHours)  from course join section on course.course_id= section.course_id join registered_courses on (registered_courses.course_id=section.course_id) where registered_courses.std_id=(%s) group by course.course_id ")
                q6 = ("select std_info.hours from std_info where std_info.std_id = (%s)")

                v6 = (std_id)
                cursor.execute(q6, v6)
                dd = cursor.fetchone()[0]
                temp = 0
                # for i in dd:
                #     sum = sum + cursor.fetchone()[1]

                print(dd)

                #noh = cursor.fetchone()[0]
                # if (noh is None):
                #   noh = 0
                currnoh = cp
                temp = dd+currnoh

                #currnoh = currnoh + noh

                if temp <= 20:

                    #                     INSERT INTO table_name (column1, column2, column3, ...)
                    # VALUES (value1, value2, value3, ...);

                    q7 = (
                        "insert into mydb.registered_courses (std_id,course_id,sec_id) values (%s,%s,%s)")
                    v7 = (std_id, cl, sl)
                    cursor.execute(q7, v7)
                    connection.commit()

                    # q8 = ("select CONCAT ('[',section_time.start_time,' - ' ,section_time.end_time,'] ',section_time.day) AS 'time'    ,section.section_id, course.noOfHours,course.course_name,section.course_id from course join section on course.course_id = section.course_id join section_time on section_time.sec_time_id=section.section_time join registered_courses on (registered_courses.sec_id = section.section_id and registered_courses.course_id=section.course_id) where registered_courses.std_id =(%s) and registered_courses.course_id =(%s) and registered_courses.sec_id = (%s)")
                    # v8 = (std_id, cl, sl)

                    q8 = ("select CONCAT ('[',section_time.start_time,' - ' ,section_time.end_time,'] ',section_time.day) AS 'time' ,section.section_id, course.noOfHours,course.course_name,section.course_id from course join section on course.course_id = section.course_id join section_time on section_time.sec_time_id=section.section_time join registered_courses on (registered_courses.sec_id = section.section_id and registered_courses.course_id=section.course_id) where registered_courses.std_id =(%s)")
                    v8 = (std_id)
                    cursor.execute(q8, v8)
                    data8 = cursor.fetchall()

                    section8 = []
                    for result in data8:
                        vaar = {
                            'time': result[0],
                            's_id': result[1],
                            'nh': result[2],
                            'cn': result[3],
                            'c_id': result[4],
                        }
                        section8.append(vaar)
                    q9 = (
                        "UPDATE std_info SET std_info.hours = (%s) WHERE std_info.std_id = (%s)")
                    v9 = (temp, std_id)
                    cursor.execute(q9, v9)

                    q10 = (
                        "UPDATE std_info SET std_info.financial_record = (%s) WHERE std_info.std_id = (%s)")
                    v10 = (fr1, std_id)
                    cursor.execute(q10, v10)
                    # (section8)
                    # text = "اكتملت العملية بنجاح"
                    # speak(text)
                    return jsonify("اكتملت العملية بنجاح", section8)

                else:

                    q8 = ("select CONCAT ('[',section_time.start_time,' - ' ,section_time.end_time,'] ',section_time.day) AS 'time' ,section.section_id, course.noOfHours,course.course_name,section.course_id from course join section on course.course_id = section.course_id join section_time on section_time.sec_time_id=section.section_time join registered_courses on (registered_courses.sec_id = section.section_id and registered_courses.course_id=section.course_id) where registered_courses.std_id =(%s)")
                    v8 = (std_id)
                    cursor.execute(q8, v8)
                    data8 = cursor.fetchall()

                    section8 = []
                    for result in data8:
                        vaar = {
                            'time': result[0],
                            's_id': result[1],
                            'nh': result[2],
                            'cn': result[3],
                            'c_id': result[4],
                        }
                    section8.append(vaar)

                    # text = "انت لا تستطيع تسجيل اكثر من 20 ساعة تتهورش"
                    # speak(text)

                    return jsonify(
                        "انت لا تستطيع تسجيل اكثر من 20 ساعة...تتهورش", section8)

            else:
                q8 = ("select CONCAT ('[',section_time.start_time,' - ' ,section_time.end_time,'] ',section_time.day) AS 'time' ,section.section_id, course.noOfHours,course.course_name,section.course_id from course join section on course.course_id = section.course_id join section_time on section_time.sec_time_id=section.section_time join registered_courses on (registered_courses.sec_id = section.section_id and registered_courses.course_id=section.course_id) where registered_courses.std_id =(%s)")
                v8 = (std_id)
                cursor.execute(q8, v8)
                data8 = cursor.fetchall()

                section8 = []
                for result in data8:
                    vaar = {
                        'time': result[0],
                        's_id': result[1],
                        'nh': result[2],
                        'cn': result[3],
                        'c_id': result[4],
                    }
                    section8.append(vaar)
                #currnoh = currnoh - noh
                # text = "السجل المالي غير كافي"
                # speak(text)

                return jsonify(
                    "السجل المالي غير كافي", section8)
        else:
            #currnoh = currnoh - noh
            q8 = ("select CONCAT ('[',section_time.start_time,' - ' ,section_time.end_time,'] ',section_time.day) AS 'time' ,section.section_id, course.noOfHours,course.course_name,section.course_id from course join section on course.course_id = section.course_id join section_time on section_time.sec_time_id=section.section_time join registered_courses on (registered_courses.sec_id = section.section_id and registered_courses.course_id=section.course_id) where registered_courses.std_id =(%s)")
            v8 = (std_id)
            cursor.execute(q8, v8)
            data8 = cursor.fetchall()

            section8 = []
            for result in data8:
                vaar = {
                    'time': result[0],
                    's_id': result[1],
                    'nh': result[2],
                    'cn': result[3],
                    'c_id': result[4],
                }
                section8.append(vaar)
            # text = "هذا المساق يتعارض مع مساق اخر في نفس الوقت"
            # speak(text)

            return jsonify(
                "هذا المساق يتعارض مع مساق اخر في نفس الوقت", section8)

    else:
        #currnoh = currnoh - noh
        q8 = ("select CONCAT ('[',section_time.start_time,' - ' ,section_time.end_time,'] ',section_time.day) AS 'time' ,section.section_id, course.noOfHours,course.course_name,section.course_id from course join section on course.course_id = section.course_id join section_time on section_time.sec_time_id=section.section_time join registered_courses on (registered_courses.sec_id = section.section_id and registered_courses.course_id=section.course_id) where registered_courses.std_id =(%s)")
        v8 = (std_id)
        cursor.execute(q8, v8)
        data8 = cursor.fetchall()

        section8 = []
        for result in data8:
            vaar = {
                'time': result[0],
                's_id': result[1],
                'nh': result[2],
                'cn': result[3],
                'c_id': result[4],
            }
            section8.append(vaar)
            # connection.close()
        # text = "انت بالفعل مسجل في هذا المساق"
        # speak(text)

        return jsonify("انت بالفعل ملتحق بشعبة من هذا المساق يجب عليك حذف المساق ثم اعادة الالتحاق بشعبة اخرى", section8)

    # if (data2 == 0):
    #     return jsonify("success")
    # else:
    #     return jsonify("wrong")


@app.route("/delete_ajax", methods=['POST'])
def delete_ajax():
    cl = request.form['cl']
    sl = request.form['sl']
    std_id = request.form['std_id']

    q4 = (
        "select std_info.financial_record from std_info where std_info.std_id=(%s)")
    v4 = (std_id)
    cursor.execute(q4, v4)
    fr = cursor.fetchone()[0]
    fr1 = fr

    q5 = ("select course.noOfHours from course where course.course_id=(%s)")
    v5 = (cl)
    cursor.execute(q5, v5)
    cp = cursor.fetchone()[0]
    print(cp)
    price = cp*24
    print(price)
    fr1 = fr1+price
    print(fr1)
    # update finincial record to the value of fr1

    q6 = ("select std_info.hours from std_info where std_info.std_id = (%s)")

    v6 = (std_id)
    cursor.execute(q6, v6)
    dd = cursor.fetchone()[0]

    temp = dd - cp

# update noOfHours to the value of the temp
    print(temp)

    q7 = (
        "delete from registered_courses where registered_courses.std_id =(%s) and registered_courses.course_id = (%s) and registered_courses.sec_id = (%s) ")
    v7 = (std_id, cl, sl)
    cursor.execute(q7, v7)
    connection.commit()

    # q8 = ("select CONCAT ('[',section_time.start_time,' - ' ,section_time.end_time,'] ',section_time.day) AS 'time'    ,section.section_id, course.noOfHours,course.course_name,section.course_id from course join section on course.course_id = section.course_id join section_time on section_time.sec_time_id=section.section_time join registered_courses on (registered_courses.sec_id = section.section_id and registered_courses.course_id=section.course_id) where registered_courses.std_id =(%s) and registered_courses.course_id =(%s) and registered_courses.sec_id = (%s)")
    # v8 = (std_id, cl, sl)

    q8 = ("select CONCAT ('[',section_time.start_time,' - ' ,section_time.end_time,'] ',section_time.day) AS 'time' ,section.section_id, course.noOfHours,course.course_name,section.course_id from course join section on course.course_id = section.course_id join section_time on section_time.sec_time_id=section.section_time join registered_courses on (registered_courses.sec_id = section.section_id and registered_courses.course_id=section.course_id) where registered_courses.std_id =(%s)")
    v8 = (std_id)
    cursor.execute(q8, v8)
    data8 = cursor.fetchall()

    section8 = []
    for result in data8:
        vaar = {
            'time': result[0],
            's_id': result[1],
            'nh': result[2],
            'cn': result[3],
            'c_id': result[4],
        }
        section8.append(vaar)
    q9 = (
        "UPDATE std_info SET std_info.hours = (%s) WHERE std_info.std_id = (%s)")
    v9 = (temp, std_id)
    cursor.execute(q9, v9)

    q10 = (
        "UPDATE std_info SET std_info.financial_record = (%s) WHERE std_info.std_id = (%s)")
    v10 = (fr1, std_id)
    cursor.execute(q10, v10)
    # (section8)
    return jsonify("اكتملت العملية بنجاح", section8)


@app.route('/row_detail/<rowData>/<name>')
def row_detail(rowData, name):
    # q = ("SELECT classroom.room_capacity,instructor_info.inst_name,section_time.start_time,section.room_id,section.section_id FROM instructor_info JOIN section JOIN classroom JOIN course  on  section.course_id=(%s) and classroom.room_id=section.room_id and section.inst_id=instructor.inst_id ")
    q = ("SELECT section.course_id,section.section_id,section.room_id,section.section_time,section.inst_id FROM course JOIN section on course.course_id=section.course_id and section.course_id=(%s)")
    v = (rowData)
    cursor.execute(q, v)
    data = cursor.fetchall()

    q2 = ("SELECT course.course_id,course.course_name,course.noOfHours,plan.req_type FROM  course JOIN plan  on course.course_id=plan.course_id and dept_name=(%s)")
    v2 = (name)
    cursor.execute(q2, v2)
    data2 = cursor.fetchall()

    return render_template('StudentRegistration.html', value2=data, v=name, value=data2)


@app.route('/registerSection/<rowData>/<name>')
def registerSection(rowData, name):
    # q = ("SELECT classroom.room_capacity,instructor_info.inst_name,section_time.start_time,section.room_id,section.section_id FROM instructor_info JOIN section JOIN classroom JOIN course  on  section.course_id=(%s) and classroom.room_id=section.room_id and section.inst_id=instructor.inst_id ")
    q = ("SELECT section.course_id,section.section_id,section.room_id,section.section_time,section.inst_id FROM course JOIN section on course.course_id=section.course_id and section.course_id=(%s)")
    v = (rowData)
    cursor.execute(q, v)
    data = cursor.fetchall()

    q2 = ("SELECT course.course_id,course.course_name,course.noOfHours,plan.req_type FROM  course JOIN plan  on course.course_id=plan.course_id and dept_name=(%s)")
    v2 = (name)
    cursor.execute(q2, v2)
    data2 = cursor.fetchall()

    return render_template('StudentRegistration.html', value2=data, v=name, value=data2)

# @app.route("/selectSections/<name1>/<name2>/<name3>")
# def StudentRegistration(name1,name2,name3):
#     q = ("SELECT section.section_id,section.room_id,section_time.start_time,instructor_info.inst_name FROM  course JOIN plan  on course.course_id=plan.course_id and dept_name=(%s)")
#     v = (name)
#     cursor.execute(q, v)
#     data2 = cursor.fetchall()
#     return render_template("StudentRegistration.html", value=data2, v=name)


@app.route("/CourseSchedule", methods=['POST'])
def CourseSchedule():
    std_id = request.form.get("y")

    # q = (
    #     "select concat (section.full_building_name,' (',section.building,')'), CONCAT (section.building,'-' ,section.room_id) AS 'class_room',CONCAT( instructor_info.f_name ,' ', instructor_info.l_name  ) AS 'inst_name' , CONCAT ('[',section_time.start_time,' - ' ,section_time.end_time,'] ',section_time.day) AS 'time' , section.section_id,course.noOfHours,course.course_name,section.course_id from section join course on course.course_id = section.course_id join instructor_info on instructor_info.inst_id = section.inst_id join section_time on section_time.sec_time_id = section.section_time join registered_courses on (registered_courses.course_id=section.course_id and registered_courses.sec_id= section.section_id) where registered_courses.std_id=(%s)")

    # q = ("SELECT course.course_id,course.course_name,course.noOfHours,plan.req_type FROM  course JOIN plan  on course.course_id=plan.course_id ")
    q = ("SELECT course.course_id  ,   course.course_name   ,    course.noOfHours    ,     section.section_id    ,    CONCAT ('[',section_time.start_time,' - ' ,section_time.end_time,'] ',section_time.day) AS 'time'    ,     CONCAT( instructor_info.f_name ,' ', instructor_info.l_name  ) AS 'inst_name'      ,      CONCAT (section.building,'-' ,section.room_id) AS 'class_room'    ,      concat (section.full_building_name,' (',section.building,')')     from section join course on course.course_id = section.course_id join instructor_info on instructor_info.inst_id = section.inst_id join section_time on section_time.sec_time_id = section.section_time  ")

    cursor.execute(q)
    data2 = cursor.fetchall()

    q1 = ("SELECT count(*) from section join registered_courses on (section.section_id = registered_courses.sec_id and section.course_id = registered_courses.course_id)")
    cursor.execute(q1)
    noOfStudent = cursor.fetchall()

    # q1 = ("SELECT capacity from classroom join section  on (section.room_id =classroom.room_id and section.course_id = registered_courses.course_id)")

    return render_template("CourseSchedule.html", value=data2, v2=std_id)


@app.route("/afterlogin", methods=['POST'])
def afterlogin():

    id = request.form.get("number")

    b = int(id)
    q = ("SELECT * FROM  std_info WHERE std_id=(%s)")
    v = (b)
    cursor.execute(q, v)
    data = cursor.fetchall()
    return render_template("afterlogin.html", value=data)


@app.route("/financial", methods=['POST'])
def financial():
    std_id = request.form.get("x")
    q = ("select financial_record from std_info where std_info.std_id=(%s) ")
    v = (std_id)
    cursor.execute(q, v)
    data = cursor.fetchone()[0]

    return render_template("financial.html", finance=data, v2=std_id)


@app.route("/temporary_ajax", methods=['POST'])
def temporary_ajax():

    std = request.form.get("std_id")
    q=("select course_id,sec_id,noOfHours from temp_registered_courses join course on temp_registered_courses.course_id=course.course_id   join section on section.course_id=course.course_id where std_id=(%s)")
    v=(std)
    cursor.execute(q,v)
    data = cursor.fetchall
    section=[]
    for result in data:
      contents={'course':result[0],
      'section':result[1]}
     
    section.append(contents)
    return jsonify(section)
if __name__ == "__main__":
    app.run(port=9000)
