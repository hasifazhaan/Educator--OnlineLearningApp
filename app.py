import os
import json
import re
from regex import P
from werkzeug.utils import secure_filename
from flaskext.mysql import MySQL
from flask import (
    Flask,
    render_template,
    request,
    flash,
    url_for,
    redirect,
    session,


    abort,
    jsonify
)
from datetime import date, datetime
from csv import writer
import uuid
from operator import itemgetter


# derived modules
from backend.user.loginconfig import login_valid_user,newuser, userinfo
from MlModels.course_recommendation import recommend
from backend import searchcourse
from backend.get_data import coursedata, create_course_data, create_cards_details, deduct_balance, mycourses


app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'educator'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['UPLOAD_FOLDER'] = 'static/modules'
app.config['UPLOAD_FOLDER_IMAGE'] = 'static/images/courseimage'
app.config['UPLOAD_EXTENSIONS'] = ['.MP4', '.mp4', '.jpg', '.png']
app.config['CSVFILE'] = 'dataset'

mysql = MySQL(app)
conn = mysql.connect()

cursor = conn.cursor()

# db = SQLAlchemy(app)


@app.route('/', methods=('GET', 'POST'))
def indexpage():
    return render_template("index.html")


@app.route("/homepage", methods=['POST', 'GET'])
def homepage():
    try:
        if session['username']:
            return render_template("home.html", courselist=create_course_data(conn, session['username']))
        else:
            return redirect(url_for("indexpage"))
    except KeyError as k:
        return redirect(url_for("indexpage"))

# user mgmt start

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop("username", None)
    return render_template("index.html")

@app.route('/login', methods=('POST', 'GET'))
def login_creds():
    if request.method == 'POST':
        uname = request.form.get('username')
        password = request.form.get('password')
        validation = login_valid_user(uname,password,cursor,session,conn)
        if validation:
            return redirect(url_for("homepage"))  
        flash("Invalid Username/ Password")
    return render_template("index.html")
    

@app.route('/signup', methods=['POST', 'GET'])
def createuser():
    if request.method == 'POST':
        new_user = request.form.get('new_username')
        password = request.form.get('new_pass')
        conf_pass = request.form.get('conf_pass')

        if password == conf_pass:
            result = newuser(new_user,password,cursor,conn,session)
            if result:
                return render_template("signup.html")
            else:
                flash("Error While Processing Please Try Again")
                return render_template("index.html")
        else:
            flash("Confirm password do not match")
            return render_template("index.html")

    else:
        return redirect(url_for("indexpage"))


@app.route("/savedata", methods=['POST', 'GET'])
def saveData():
    if request.method == 'POST':
        Phoneno = request.form.get('Phoneno')
        Qualification = request.form.get('Qualification')
        List_interested = request.form.getlist('Interested')
        if userinfo(Phoneno,Qualification,List_interested,session['username'],conn) == False:
            return "An Error Occured Please Try Again..."
    return redirect(url_for("homepage"))

@app.route("/Continue_", methods=['POST', 'GET'])
def Continue():
    return redirect(url_for("homepage"))

# user mgmt end

#  search course


@app.route('/search_courses',methods=['POST','GET'])
def course_page():
    return render_template("search_course.html")


@app.route('/Recommend_Courses', methods=['GET', 'POST'])
def SearchCourse():
    if request.method == 'POST':
        content = request.form.get('search_input')
        courselist = create_course_data(conn, session['username'], content)
    return render_template("search_course.html", courselist=courselist)


# payment
@app.route('/payment/<course_id>')
def payment_course(course_id):
    courselist = create_course_data(
        conn, session['username'], recommend=False, course_id=course_id)
    card_list = create_cards_details(session['username'], cursor, conn)
    return(render_template('payment_page.html', cards=card_list, i=courselist[0]))


@app.route('/addcard/<course_id>', defaults={'course_id': None})
@app.route('/addcard/<course_id>')
def addcard(course_id):
    return(render_template('addcard_page.html', course_id=course_id))


@app.route('/getcarddetails/<course_id>', defaults={'course_id': None})
@app.route('/getcarddetails/<course_id>', methods=['POST'])
def carddetails(course_id):
    if request.method == 'POST':
        cardholder = request.form.get('cardholder')
        cardno = request.form.get('cardno')
        expire = request.form.getlist('expdate')[0]
        cvv = request.form.getlist('cvv')[0]
        bal = 2000
        try:
            sqlquery = f"INSERT INTO payment_cards VALUES('{session['username']}','{cardholder}','{cardno}','{expire}','{cvv}',{bal})"
            cursor.execute(sqlquery)
            conn.commit()
        except:
            return("somthing Went Wrong Try Later")
        print(type(course_id))
        if course_id == 'None':
            return(redirect(url_for('payments')))
        return redirect(url_for('payment_course', course_id=course_id))


@app.route('/purchase/<course_id>', methods=['POST', 'GET'])
def purchase(course_id):
    if request.method == 'POST':
        try:
            data = request.form.getlist('radio_btn')[0]
            user_cvv = request.form.get('cvv_userside')
            course_price = request.form.get("price")
            data = json.loads(data.replace("\'", "\""))
        except IndexError as E:
            flash("Select a Card")
            return redirect(url_for('payment_course', course_id=course_id))

        month, year = data['expire'].split("/")
        expiredate = date(int(year)+2000, int(month), 1)
        todaydate = date.today()

        if expiredate < todaydate:
            flash("Card Expired")
            print("NO")
            return redirect(url_for('payment_course', course_id=course_id))

        elif str(data['cvv']) != str(user_cvv):
            flash("Invalid CVV Number")
            print(data['cvv'], user_cvv)
            return redirect(url_for('payment_course', course_id=course_id))

        elif int(data['bal']) > int(course_price):

            if deduct_balance(cursor, conn, course_price, data['no']):
                try:
                    sqlquery = f"INSERT INTO student_course VALUES('{session['username']}','{course_id}',0,0,null) "
                    print(sqlquery)
                    cursor.execute(sqlquery)
                    conn.commit()

                    return(render_template('purchased.html', transaction=True))
                except Exception as e:
                    print(str(e))                    
                    return (render_template('purchased.html', transaction=False))
        else:
            flash("Insufficient Balance")
            return redirect(url_for('payment_course', course_id=course_id))

    return redirect(url_for('payment_course', course_id=course_id))


#  Learning Page

@app.route('/learning_page')
def learning_page():
    courselist = mycourses(conn, session['username'])
    return(render_template('learning_dash_page.html', courselist=courselist))


@app.route('/modules/<course_id>')
def modules(course_id):
    #Selecting Course
    q = f"SELECT course_title FROM course_list_1 WHERE course_index = '{course_id}'"
    cursor.execute(q)
    subject = cursor.fetchone()
    
    #checking if precourse done or not
    if check_if_firsttime(course_id):
        flash("Please Do The Pre Course Test To Proceed Further")
        res = getprecourse(course_id)
        print(res,course_id)
        
        return(render_template('module.html', subjectname=subject[0], data=res))
    
    #getting userlevel
    level = getuserlevel(course_id)
    
    #getting courses based on level
    query = f"SELECT * FROM modules  where course_id = '{course_id}' and level >= '{level}'"
    cursor.execute(query)
    res = cursor.fetchall()
    
    
    #getting completed lectures
    query = f"SELECT lecture_id FROM student_learning_history WHERE username = '{session['username']}' AND course_id = '{course_id}' AND completed = 1"
    cursor.execute(query)
    data= cursor.fetchall()
    readlecture = [val for i in data for val in i]

    readingmodules = [  ]
    for i in res:
        record = list(i)
        if record[1] in readlecture:
            record.append(1)
        else:
            record.append(0)
        readingmodules.append(record)
        
        
    return(render_template('module.html', subjectname=subject[0], data=readingmodules,level = level))

def check_if_firsttime(course_id):
    query = f"SELECT count(*) FROM student_learning_history WHERE  username = '{session['username']}' AND course_id = '{course_id}' "
    cursor.execute(query)
    res = cursor.fetchone()
    if res[0] >0:
        return False
    else:
        return True
def getprecourse(course_id):
    query = f"SELECT * FROM modules WHERE course_id = '{course_id}' AND lecture_id = 0"
    cursor.execute(query)
    res = cursor.fetchall()
    return res
def getuserlevel(course_id):
    query = f"SELECT current_level FROM student_course WHERE course_id = '{course_id}' AND username = '{session['username']}'"
    cursor.execute(query)
    level = cursor.fetchall()
    return level[0][0]
    
    
    
@app.route('/readlecture',methods=['POST'])
def method_name():
    if request.method == 'POST':
        data = request.get_json()
        try:
            query = f"INSERT INTO student_learning_history VALUES ('{session['username']}','{data['course_id']}','{data['lecture_id']}','{data['level']}','{1}')"
            cursor.execute(query)
            conn.commit()
        except Exception as e:
            query = f"UPDATE student_learning_history SET completed = 1,level = '{data['level']}' WHERE username ='{session['username']}' AND course_id = '{data['course_id']}' AND lecture_id = '{data['lecture_id']}'"  
            cursor.execute(query)
            conn.commit()
        return("Done")
        
    
    
@app.route('/moduledata/<modulename>')
def moduledata(modulename):
    # query   = f"SELECT * FROM MODULES WHERE modulename = '{modulename}' GROUP BY subtype ORDER BY lecture_id"
    # cursor.execute(query)
    # conn.commit()
    # data = cursor.fetchall()

    pass

@app.route('/test/<testname>/<c_id>/<l_id>',methods=['POST','GET'])
def test(testname,c_id,l_id):
    sqlquery = f"SELECT * FROM  testquestion WHERE course_id = '{c_id}' AND lecture_id = '{l_id}' ORDER BY question_id"
    cursor.execute(sqlquery)
    conn.commit()
    data = cursor.fetchall()
    
    return (render_template('testuser.html',data = data,cid=c_id,lid=l_id))



@app.route('/settings',methods = ['POST','GET'])
def settings():
    try:
        username = session['username']
        query =  f"SELECT * FROM userlogin  WHERE username = '{username}'"
        cursor.execute(query)
        conn.commit()
        data = cursor.fetchall()[0]
        print(data)
    except Exception as e:
        print(str(e))
        flash("Error. Please Try Later ...")
    return(render_template('setting.html',data = data))


@app.route('/setuserimage',methods=['POST','GET'])
def setuserimage():
    username = session['username']
    image = request.get_json();
    try:
        query =  f"UPDATE userlogin SET image_url = '{image['img']}' WHERE username = '{username}'"
        cursor.execute(query)
        conn.commit()
        flash("Successfully Updated...")
        session['image'] = image['img']
    except Exception as e:
        print(str(e))
        flash("Error. Please Try Later ...")
    return jsonify(success=True)

@app.route('/changepass',methods=['POST'])
def changepass():
    if request.method == 'POST':
        username = session['username']
        data = request.get_json();
    try:
        query =  f"UPDATE userlogin SET password = '{data['password']}' WHERE username = '{username}'"
        cursor.execute(query)
        conn.commit()
        flash("Successfully Updated...")
    except Exception as e:
        print(str(e))
        flash("Error. Please Try Later ...")
    return jsonify(success=True)

@app.route('/changedetails',methods=['POST'])
def changedetails():
    if request.method == 'POST':
        phoneno = request.form.get('phno');
        qual = request.form.get('qual')
        interest = request.form.get('interest')
    try:
        query =  f"UPDATE userlogin SET qual = '{qual}', phoneno = '{phoneno}',interest = '{interest}' WHERE username = '{session['username']}'"
        cursor.execute(query)
        conn.commit()
        flash("Successfully Updated...")
    except Exception as e:
        print(str(e))
        flash("Error. Please Try Later ...")
    return(redirect('settings'))



@app.route('/payments',methods=['POST','GET'])
def payments():
    try:
        query =  f"SELECT * FROM payment_cards WHERE username = '{session['username']}'"
        cursor.execute(query)
        conn.commit()
        data = cursor.fetchall()
        print(data[0])
        
    except Exception as e:
        print(str(e))
        flash("Error. Please Try Later ...")
    
    return(render_template('payments.html',cards = data))


@app.route('/analize',methods=['POST','GET'])
def analize():
    return (render_template('analize.html'))
 


@app.route('/timeslogin',methods=['POST','GET'])
def timeslogin():      
    if request.method =='POST':
        val =[1]
        try:
            q = f"SELECT sum(times),MONTH(cdate) FROM timeslogin  WHERE username = '{session['username']}'  GROUP BY MONTH(cdate)"
            cursor.execute(q)
            res = cursor.fetchall()
            val = [i[0] for i in res]
        except Exception as e: 
            print(str(e)) 
        return jsonify(data = val)
    else:
        return "No"

@app.route('/usercourse',methods = ['POST','GET'])
def usercourse():
    coursedata = [0]
    sql1 = f"SELECT count(course_id),course_id FROM student_learning_history WHERE username = '{session['username']}' GROUP BY course_id" 
    cursor.execute(sql1)
    conn.commit()
    res = cursor.fetchall()
    if request.method =='POST':
        try:
            coursedata = [] 
            for i in res: 
                sql = f"SELECT course_title FROM course_list_1 where course_index = '{i[1]}'"
                cursor.execute(sql)
                conn.commit()
                data = cursor.fetchall()[0][0]
                details = [i[0],data]
                coursedata.append(details)   
        except Exception as e:   
            print(str(e)) 
        return jsonify(data = coursedata)
    elif request.method == 'GET':
        coursedata = []
        learning = []
        for i in res:
            sql = f"SELECT count(lecture_id),course_id FROM modules where course_id = '{i[1]}' GROUP BY subtype"
            cursor.execute(sql)
            conn.commit()
            data = cursor.fetchall()
            temp = []
            
            sql2  =  f"SELECT level from student_learning_history WHERE username  = '{session['username']}' and course_id = '{i[1]}'"
            cursor.execute(sql2)
            conn.commit()
            data1 = cursor.fetchall()
            val = [i[0] for i in data1]
            learning.append(val)
            
            for i in data:
                temp.append(i[0])
            coursedata.append(temp)
        
        return jsonify(data = [coursedata,learning])
    
    
@app.route('/alluseraccess',methods = ['POST','GET'])
def alluseraccess():
    if request.method =='POST':
        val =[1]
        try:
            q = f"SELECT sum(times),MONTH(cdate) FROM timeslogin GROUP BY MONTH(cdate)"
            cursor.execute(q)
            res = cursor.fetchall()
            val = [i[0] for i in res]
            print(res)
            sql = f"SELECT count(username) FROM userlogin "
            cursor.execute(sql)
            no = cursor.fetchall()[0][0]
            
        except Exception as e: 
            print(str(e)) 
        return jsonify(data = [val,no])
    else:
        return "No"
    
    
@app.route('/analizeadmin')
def analizeadmin():
    return render_template("admin/analize.html")
    
@app.route('/top10course',methods=['POST'])
def top10course():
    sql = f"SELECT course_id from student_course ORDER BY course_id"
    cursor.execute(sql)
    no = cursor.fetchall()
    courseno = []
    for i in no:
        courseno.append(i[0])
    val = [ [l, courseno.count(l)] for l in set(courseno)]
    top10key = sorted(val, key=itemgetter(1),reverse=True)
    toplabel = []
    topval = []
    for i,val in enumerate (top10key):
        sql1  = f"SELECT course_title FROM course_list_1 WHERE course_index = '{val[0]}'" 
        cursor.execute(sql1)
        name = cursor.fetchall()[0][0]
        topval.append(val[1])
        toplabel.append(name)
        top10 = [toplabel[:10],topval[:10]]
    return jsonify(data = top10)


@app.route('/topuser',methods=['POST'])
def topuser():
    sql = f"SELECT username,times FROM timeslogin GROUP BY username ORDER BY cdate  DESC"
    cursor.execute(sql)
    no = cursor.fetchall()
    label = []
    val = []
    for i in no:
        label.append(i[0])
        val.append(i[1])
    res = [label,val]
    return jsonify(data = res)

@app.route('/usercompleted',methods=['POST'])
def usercompleted():
    sql = f"SELECT a.username,b.course_title FROM student_course as a INNER JOIN course_list_1 as b ON a.course_id = b.course_index WHERE a.completed = 1"
    cursor.execute(sql)
    no = cursor.fetchall()
    return jsonify(data = no)


@app.route('/userfailed',methods=['POST'])
def userfailed():
    sql = f"SELECT DISTINCT (course_id),lecture_id, count(lecture_id) FROM student_learning_history WHERE level = -1"
    cursor.execute(sql)
    ans =  cursor.fetchall()
    coursename = []
    lecture_id = []
    val = []
    
    for i in ans:
        sql2 = f"SELECT course_title FROM course_list_1 WHERE course_index = '{i[0]}'"
        print(sql2)
        cursor.execute(sql2)
        coursename.append(cursor.fetchall()[0][0])
        lecture_id.append(i[1])
        val.append(i[2])
        
    courselist = [coursename,lecture_id,val]
    print(courselist)      
    return jsonify(data = courselist)

@app.route('/admin_login',methods = ['POST',"GET"])
def admin_login():
    if request.method == "GET":
        return render_template('admin/admin_login.html')
    elif request.method == 'POST':
        username = request.form.get('usrname');
        passwd = request.form.get("pass")
        sql = f"SELECT COUNT(*) FROM admin_login WHERE username = '{username}' AND password = '{passwd}'"
        cursor.execute(sql)
        row = cursor.fetchall()[0][0]
        if row :
            session['admin'] = "Admins"
            return redirect(url_for('admin_home'))
        else:
            flash("Invalid username or password")
            return render_template("admin/admin_login.html")




@app.route('/admin_home')
def admin_home():
    if session['admin']:
        return(render_template('admin/admin_home.html'))
    else:
        return redirect(url_for('admin_login'))


@app.route('/getcouorseno', methods=['POST', 'GET'])
def getcouorseno():
    try:
        sqlquery = f"SELECT course_index,image_url,course_title,price,level,content_duration,subject FROM course_list_1 "
        cursor.execute(sqlquery)
        row = cursor.fetchall()
        
    except Exception as e:
        flash("Error Occured ..")
        print(str(e)) 
    return jsonify(result=row)


@app.route('/getlecturecount', methods=['POST', 'GET'])
def lecturecount():
    if request.method == "POST":
        c_id = request.get_json()
        query = f"SELECT MAX(lecture_id) FROM modules WHERE course_id = '{c_id['c_id']}' "
        cursor.execute(query) 
        row = cursor.fetchall()
    return jsonify(l_id=row[0]) 


@app.route('/getcoursecount', methods=['GET'])
def getcoursecount():
    if request.method == "GET": 
        c_id = request.get_json() 
        query = f"SELECT count(course_index) FROM course_list_1"
        cursor.execute(query)
        row = cursor.fetchall()
    return jsonify(c_id=row[0])


@app.route('/addcourse', methods=['POST', 'GET'])
def addcourse():
    if request.method == "POST":
        c_id = request.form.get('c_id')
        cname = request.form.get('cname')
        diff = request.form.get('difficulty')
        price = request.form.get('price')
        subject = request.form.get('subject')
        duration = str(request.form.get('duration'))+" hour"
        image_loc = request.files['image_loc']
        filename = secure_filename(image_loc.filename)

        if diff == '0':
            diff = 'Beginner Level'
        elif diff == '1':
            diff = 'Intermediate Level'
        elif diff == '2':
            diff == 'Expert Level'
        else:
            diff = 'All Levels'
        date = datetime.now()
        year = str(date.date().year)
        print(year)
        # ,course_title,is_paid,price,num_reviews,level,subject,year,convertedtime,Bag_Of_Words,Words_Vector
        data = [c_id, cname, '1.0', price, 45, diff,
                subject, year, 204, cname.lower(), 0.0]
        try:
            sqlquery = f"INSERT INTO course_list_1(`course_index`, `course_title`, `price`, `level`, `content_duration`, `subject`, `year`, `image_url`) VALUES({c_id},'{cname}','{price}','{diff}','{duration}','{subject}','{year}','{filename}')"
            cursor.execute(sqlquery)
            conn.commit()
            flash("Course Added Sucessfully..")
            with open(app.config['CSVFILE']+'/course_list.csv', 'a', newline='') as f_object:
                writer_object = writer(f_object)
                writer_object.writerow(data)
                f_object.close()
                print("Added")
        except Exception as e:
            flash("Error Occured ..")
            print(str(e))
    return(redirect(url_for('admin_home')))


@app.route('/addmodule', methods=['POST', 'GET'])
def addmodule():
    if request.method == 'POST':
        c_id = request.form.get('c_id')
        l_id = request.form.get('l_id')
        module_name = request.form.get('m_name')
        content = request.form.get('content')
        level = request.form.get('level')
        video_loc = request.files['video_loc']
        filename = secure_filename(video_loc.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            video_loc.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            loc = app.config['UPLOAD_FOLDER']+"/"+filename
            try:
                sqlquery = f"INSERT INTO modules VALUES({c_id},{l_id},'s1','{module_name}','{content}','{loc}','{level}')"
                cursor.execute(sqlquery)
                conn.commit()
                flash("Module Added Sucessfully..")
            except Exception as e:
                flash("Error Occured ..")

    return(redirect(url_for('admin_home')))


@app.route('/deletecourse', methods=['POST'])
def deletecourse():
    c_id = request.form.get('c_id')
    try:
        query = f"DELETE FROM course_list_1 WHERE course_index = '{c_id}'"   
        cursor.execute(query)
        conn.commit()   
        # lines = list()
        # members = int(c_id)+7
        # with open(app.config['CSVFILE']+'/course_list.csv', 'r') as readFile:
        #     reader = csv.reader(readFile)
        #     for row in reader:
        #         lines.append(row)
        #     for field in row:
        #         if field == members:
        #             lines.remove(row)
        # with open(app.config['CSVFILE']+'/course_list.csv', 'w') as writeFile:
        #     writer = csv.writer(writeFile)
        #     writer.writerows(lines)

        flash("course Deleted Sucessfully..")
    except Exception as e:
        print(str(e))
        flash("Error in Deleting Notes")
    return(redirect(url_for('admin_home')))

@app.route('/updatecourse',methods=['POST','GET'])
def updatecourse():
    if request.method == 'POST':
        c_id = request.form.get('c_id')
        module_name = request.form.get('cname')   
        content = request.form.get('duration')
        level = request.form.get('clevel')
        price = request.form.get('price')
        subject = request.form.get('subject') 
        try:	
            query = f"UPDATE `course_list_1` SET`course_title`='{module_name}',`price`='{price}',`level`='{level}',`content_duration`='{content}',`subject`='{subject}' WHERE course_index = '{c_id}'"
            cursor.execute(query)
            conn.commit()
            flash("Success - Course Updated")
        except Exception as e:
            print(str(e))
            flash("Error In Updating Course")
    return(redirect(url_for('admin_home')))

@app.route('/getmoduleindex',methods=['POST'])
def getmoduleindex():
    c_id = request.get_json()
    query = f"SELECT lecture_id FROM modules WHERE course_id ='{c_id['c_id']}'"
    cursor.execute(query)
    row = cursor.fetchall()
    return jsonify(result=row)

@app.route('/getlecturename',methods=['POST'])
def getlecturename():
    value = request.get_json()
    query = f"SELECT modulename,video FROM modules WHERE course_id ='{value['c_id']}' AND lecture_id='{value['l_id']}'"
    cursor.execute(query)
    row = cursor.fetchall()
    print(row)
    return jsonify(result=row)


@app.route('/deletemodules',methods=['POST'])
def deletemodules():
    if request.method == 'POST':
        c_id = request.form.get('c_id')
        l_id = request.form.get('l_id')
        try:
            query = f"DELETE FROM modules WHERE course_id = '{c_id}' AND lecture_id = '{l_id}'"
            cursor.execute(query)
            conn.commit()
            flash("Module Deleted Sucessfully..")
        except Exception as e:
            print(str(e))
            flash("Error in Deleting Module")
    return(redirect(url_for('admin_home')))

 
@app.route('/testevaluate',methods=['POST'])
def testevaluate():
    if request.method == 'POST':
        no_of_question = int(request.form.get('no_of_question'))
        c_id = request.form.get("cid")
        l_id = request.form.get("lid")
        optionname = ["o" + str(i) for i in range(1,no_of_question+1)]
        answer_user = []
        for i in optionname:
            opt = request.form.get(i)
            answer_user.append(opt)
        realanswer =  request.form.getlist('correctanswer')
        level = request.form.getlist('weight')
        weights = []
        for i in level:
            if i== '0':
                weights.append(0.3)
            elif i == '1':
                weights.append(0.5)
            else:
                weights.append(0.9)
        totalmarks = sum(weights)
        obtained = 0
        for i in zip(answer_user,realanswer,weights):
            if i[0]==i[1]:
                obtained += i[2]
        percentage = obtained/totalmarks
        summary= "Pass" 
        if percentage > 0.85:
            level = 2
            
        elif percentage < 0.85 and percentage >0.65:
            level =1
        elif percentage < 0.65 and percentage > 0.45:
            level = 0 
        else:
            level =-1
            summary= "Failed"
            
        query = f"INSERT INTO test_history VALUES ('{session['username']}', '{c_id}','{l_id}','{obtained}','{summary}')"
        cursor.execute(query)
        conn.commit() 
        result = [round(totalmarks,1),round(obtained,1), summary,level,c_id,l_id]
        if level >=0:
            sql = f"SELECT subtype FROM modules WHERE course_id = '{c_id}' AND lecture_id = '{l_id}'"
            cursor.execute(sql)
            conn.commit() 
            val = cursor.fetchall()[0][0];
            if val =='Finaltest':
                cert_id = uuid.uuid1()
                sql2 = f"UPDATE student_course SET completed = 1, cert_id = '{cert_id}' WHERE username = '{session['username']}' AND course_id = '{c_id}'"
                cursor.execute(sql2)
                conn.commit() 
                completedmodule(c_id,l_id,level,1)
                return(redirect(url_for('finalcomplete',id = cert_id)))
            
    return(render_template('testresult.html',data = result))




@app.route('/setlevel/<level>/<course_id>/<lecture_id>',methods = ['POST','GET'])
def setlevel(level,course_id,lecture_id):
    if int(level) >=0:
        completedmodule(course_id,lecture_id,level,1)
    else:
        completedmodule(course_id,lecture_id,level,0)
    
    if int(level) < 0:
        level = 0
    query = f"  UPDATE student_course SET current_level = '{level}' WHERE course_id = '{course_id}' AND username = '{session['username']}' "
    cursor.execute(query)
    conn.commit()
    return(redirect(url_for('modules',course_id = course_id )))



def completedmodule(c_id,l_id,level,completed):
    try:
        try:
            query = f" INSERT INTO  student_learning_history VALUES('{session['username']}','{c_id}','{l_id}','{level}','{completed}')"
            cursor.execute(query)
            conn.commit()
            print("Done")
        except Exception as e:
            print(str(e))
            query = f"UPDATE student_learning_history SET level = '{level}',completed = '{completed}' WHERE username = '{session['username']}'AND course_id = '{c_id}' AND lecture_id = '{l_id}' "
            cursor.execute(query)
            conn.commit()
            print("Done exec")
            
    except Exception as e:
        print("err")
        return("You Already Completed Pre Course Test")
        
        
        return True



@app.route('/finalcomplete/<id>',methods=['POST','GET'])
def finalcomplete(id):
    return render_template("finalcomplete.html",id = id)

@app.route('/viewcertificate/<id>',methods = ['POST','GET'])
def viewcertificate(id):
    print(id)
    sql = f"SELECT  * FROM student_course WHERE cert_id = '{id}' "
    cursor.execute(sql)
    conn.commit()
    data = cursor.fetchall()[0]
    print(data)
    course_id = data[1]
    name = data[0].split("@")[0]
    sql2  = f"SELECT course_title FROM course_list_1 WHERE course_index = '{course_id}'"
    cursor.execute(sql2)
    conn.commit()
    coursename = cursor.fetchall()[0][0]
    details = {
        "name": name,
        "coursename":coursename,
        "cert_id": id
    }
    return render_template('certificate.html',data = details)


@app.route('/getcert_id',methods=['POST'])
def getcert_id():
    data = request.get_json()
    username = session['username']
    print(data['c_id'])
    sql = f"SELECT cert_id FROM student_course WHERE username = '{username}' AND course_id = '{data['c_id']}' "
    cursor.execute(sql)
    conn.commit()
    res = cursor.fetchall()
    return jsonify(id = res[0][0])
    

@app.route('/addtest',methods=['POST'])
def addtest():
    course_id = request.form.get('c_id')
    lecture_id = request.form.get('l_id')
    questions = range(int(request.form.get('no_of_question')))
    qp_name = request.form.get('q_name')
    qtype = request.form.get('papertype')
    print(qtype)
    qp = ['q' + str(i) for i in questions]
    question_list= list()
    choices = []
    right_ans = []
    level = []
    for val,qp_no in enumerate(qp):
        q = request.form.get(qp_no)      
        options = request.form.getlist('answer'+str(val))
        correct = request.form.getlist('check'+str(val))
        l = request.form.get('l'+str(val))
        question_list.append(q)
        choices.append(options)
        right_ans.append(correct)
        level.append(l)
    for q_id,i in enumerate(zip(question_list,choices,right_ans,level)):
        q_id += 1
        c_question = i[0]
        options_str = ",".join(i[1])
        crt_options = "".join(i[2])
        completed = False
        l_level = i[3]
        try:
            sqlquery = f"INSERT INTO testquestion VALUES ('{course_id}','{lecture_id}','{q_id}','{qp_name}','{c_question}','{options_str}','{crt_options}','{l_level}')"
            cursor.execute(sqlquery)
            conn.commit()
            completed = True
            print("Done 1")
        except Exception as e:
            print(str(e))
            flash("Error While Adding Test..")
    if completed:
        try:
            sql2 = f"INSERT INTO modules VALUES ('{course_id}','{lecture_id}','{qtype}','{qp_name}','{qtype}','0','3')"
            cursor.execute(sql2)
            conn.commit()
            flash("Module Added Sucessfully..(Test)")
        except Exception as e:
            print(str(e))
            flash("Error While Adding Test..")
            
  
    return(redirect('admin_home'))
    
    
    
if __name__ == "__main__":

    app.run(debug=True
            # ,host='192.168.242.30'
            )
