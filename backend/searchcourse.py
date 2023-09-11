from MlModels.course_recommendation import recommend
from distutils.log import debug
from flaskext.mysql import MySQL
from flask import (
    Flask,
    render_template,
    request,
    flash,
    url_for,
    redirect,
    session
)


def recommend_course_data(conn,session_user_interests):
    cursor = conn.cursor()
    indexs = recommend(session_user_interests)
    try:
        sqlquery = f"SELECT * FROM course_list_1 WHERE  course_index IN ({indexs})"
        cursor.execute(sqlquery)
        conn.commit()
        row = cursor.fetchall()
    except:
        row = [None]
    cursor.close()
    return row;