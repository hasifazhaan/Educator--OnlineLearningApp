from datetime import datetime

def login_valid_user(usr,passwd,cursor,session,conn):
    cursor.execute( f"SELECT count(*) FROM userlogin WHERE username = '{usr}'AND password = '{passwd}' ")
    row = cursor.fetchone()
    if row[0] == 0:
        return False
    
    session['username'] = usr
    sql = f"SELECT image_url FROM userlogin WHERE username = '{session['username']}'"
    cursor.execute(sql)
    conn.commit()
    data = cursor.fetchone()[0]
    session['image'] =  data
    addlogintime(usr,cursor,conn)
    return True

def addlogintime(usr,cursor,conn):
    tdate = datetime.today().strftime('%Y-%m-%d')
    try:
        sql = f"INSERT INTO timeslogin VALUES  ('{usr}' , 1 , '{tdate}')"
        cursor.execute(sql)
        conn.commit()
        print("Logged In")
    except Exception as e: 
        sql = f"UPDATE timeslogin SET times  = times + 1  WHERE  cdate = '{tdate}' AND  username = '{usr}' "
        cursor.execute(sql)
        conn.commit()
    return



def newuser(usr,passwd,cursor,conn,session):
    try:
        sql = f"INSERT INTO userlogin (username , password) VALUES ('{usr}','{passwd}')"
        cursor.execute(sql)
        conn.commit()
        session["username"] = None
        session['username'] = usr
        return True
    except Exception as e:
        print(str(e))
        return False

    
def userinfo(Phoneno,Qualification,List_interested,usr,conn):
    try:
        cursor = conn.cursor()
        Interested = ",".join(List_interested)
        sql = f"UPDATE userlogin SET phoneno = '{Phoneno}', qual = '{Qualification}', interest = '{Interested}',image_url = '/static/users/default.png' WHERE username = '{usr}'"
        cursor.execute(sql)
        conn.commit()
        print("True")
        return True
    except Exception as e:
        print("Problem inserting into db: " + str(e))
        return False