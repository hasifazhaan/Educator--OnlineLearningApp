from backend import searchcourse


def get_user_interest(cursor, conn, username):
    select_interest = f"SELECT  interest FROM userlogin WHERE username = '{username}'"
    cursor.execute(select_interest)
    conn.commit()
    row1 = cursor.fetchone()
    session_user_interests = " ".join(list(row1))
    return session_user_interests


def checkifregistered(cursor, username, id):
    sql = f"SELECT count(course_id) FROM student_course WHERE username = '{username}' AND course_id = {id}"
    cursor.execute(sql)
    row = cursor.fetchone()
    if row[0] == 0:
        registered = False
    else:
        registered = True
    return registered

 
def create_course_data(conn, username, keyword="interest", recommend=True, course_id=-1):
    cursor = conn.cursor()
    courselist = []
    if recommend:
        if keyword == "interest":
            user_interest = get_user_interest(cursor, conn, username)
        else:
            user_interest = keyword
        recommend_list = searchcourse.recommend_course_data(
            conn, user_interest)
    else:
        sqlquery = f"SELECT * FROM course_list_1 WHERE  course_index = '{course_id}'"
        cursor.execute(sqlquery)
        conn.commit()
        recommend_list = cursor.fetchall()
    try:
        if recommend_list[0] != None:
            for i in recommend_list:
                id = i[0]
                coursename = i[1]
                price = i[2]
                review = i[3]
                level = i[4]
                content_dur = i[5]
                sub = i[6]
                year = i[7]
                image = i[8]
                dictionery_course = {
                    "id": id,
                    "url": image,
                    "course_title": coursename,
                    "description": f"{review} Reviews\n{content_dur} Duration\n Subject-{sub}\n {year} \n level {level}",
                    "price": price,
                    "registered": checkifregistered(cursor, username, id)
                }
                courselist.append(dictionery_course)
        else:
            courselist = False
    except Exception as e:
        print(str(e))
    return courselist


    
def create_cards_details(username, cursor, conn):
    try:
        sqlquery = f"SELECT * FROM payment_cards WHERE username = '{username}'"
        cursor.execute(sqlquery)
        conn.commit()
        cards = cursor.fetchall()
    except:
        return("Error")

    card_list = []
    if cards:
        for i in cards:
            cardname = i[1]
            cardno = i[2]
            expire = i[3]
            cvv = i[4]
            bal = i[5]
            cards_dict = {
                "name": cardname,
                "no": cardno,
                "expire": expire,
                "cvv": cvv,
                "bal": bal
            }
            card_list.append(cards_dict)
    else:
        card_list = False
    return card_list


def deduct_balance(cursor, conn, course_price, cardno):
    res = False
    try:
        sqlquery = f"UPDATE payment_cards SET balance = balance - {int(course_price)}  WHERE cardnumber = '{cardno}'"
        cursor.execute(sqlquery)
        conn.commit()
        res = True
    except:
        return("something Went Wrong Try Later")
    return(res)

def coursedata(conn,course_index):
    try:
        cursor = conn.cursor()
        sqlquery = f"SELECT * FROM course_list_1 WHERE course_index IN ({course_index})"
        cursor.execute(sqlquery)
        conn.commit()
        my_course = cursor.fetchall()
        cursor.close()
    except Exception as e:
        print(str(e))
        return [None]
    if my_course[0] != None:
        courselist = []
        for i in my_course:
            id = i[0]
            coursename = i[1]
            price = i[2]
            review = i[3]
            level = i[4]
            content_dur = i[5]
            sub = i[6]
            year = i[7]
            image = i[8]
            dictionery_course = {
                "id": id,
                "url": image,
                "course_title": coursename,
                "description": f"{review} Reviews\n{content_dur} Duration\n Subject-{sub}\n {year} \n level {level}",
                "price": price
            }
            courselist.append(dictionery_course)
    else:
        courselist = False
    return courselist
    
    
def mycourses(conn, username):
    cursor = conn.cursor()
    sqlquery = f"SELECT course_id FROM student_course WHERE username = '{username}'"
    cursor.execute(sqlquery)
    conn.commit()
    course_index = cursor.fetchall()
    l = []
    for i in course_index:
        l.append(i[0])
    l = list(set(l))
    strlist = ",".join(l)    
    cursor.close()
    course = coursedata(conn,strlist)
    return course
    
