from flask import Flask, render_template, jsonify #, url_for, request, redirect
#from flask_sqlalchemy import SQLAlchemy
#from flask_mysqldb import MySQL
import mysql.connector
# import datetime
import json
import requests


app = Flask(__name__)
myDb = mysql.connector.connect(host='10.0.0.69',user='root',port='3306', password='pmwpmwpmw',database='tempLog')
cursor = myDb.cursor()


#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#mydb = mysql.connector.connect(host='10.0.0.69',user='root',, password='pmwpmwpmw',database='tempLog')
#mycursor = self.mydb.cursor()
#app.config['MYSQL_HOST'] = '10.0.0.69'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'pmwpmwpmw'
#app.config['MYSQL_DB'] = 'flask'
#app.config['MYSQL_PORT'] = '3306'

#mysql = MySQL(app)


statusSet = None
@app.route('/', methods=['POST', 'GET'])
def index():
    sql = "SELECT * FROM `thermData` ORDER BY `thermData`.`Date` DESC, `thermData`.`Time` DESC LIMIT 1"
    cursor.execute(sql)
    result = cursor.fetchall()

    if result[0][4] == 1:
        furnaceStatus = "ON"
    else:
        furnaceStatus = "OFF"

    date = result[0][0].strftime("%b %-d, %Y")
    time = str(result[0][1])
    
    statusSet = {"setTemp" : result[0][3], "upstairsTemp" : result[0][2], "downstairsTemp" : "coming soon!", "furnaceStatus" : furnaceStatus, "date" : date, "time": time}

    return render_template('index.html', **statusSet)

@app.route('/api/currentStatus', methods=['GET'])
def currentStatus():
        # get the most recent data record
    sql = "SELECT * FROM `thermData` ORDER BY `thermData`.`Date` DESC, `thermData`.`Time` DESC LIMIT 1"
    cursor.execute(sql)
    result = cursor.fetchall()

    if result[0][4] == 1:
        furnaceStatus = "ON"
    else:
        furnaceStatus = "OFF"

    date = result[0][0].strftime("%b %-d, %Y")
    time = str(result[0][1])
    
    statusSet = {"setTemp" : result[0][3], "upstairsTemp" : result[0][2], "downstairsTemp" : "coming soon!", "furnaceStatus" : furnaceStatus, "date" : date, "time": time}
    return jsonify(statusSet)



    # if request.method == 'POST':
    #     task_content = request.form['content']

    #     try:
    #         return redirect('/login')
    #     except:
    #         return 'There was an issue adding your task'
    # else:
    # return 'Bowser fucking sucks'

# @app.route('/form')
# def form():
#     return render_template('form.html')
 
# @app.route('/login', methods = ['POST', 'GET'])
# def login():
#     if request.method == 'GET':
#         return redirect('/form')
     
#     if request.method == 'POST':
#         name = request.form['name']
#         age = request.form['age']
#         cursor = mydb.cursor()
#         sql = "INSERT INTO Furnace_Log_Test (date, time, status) VALUES (%s, %s, %s)"
#         val = ('2021-05-13', '10:52:01', 0)
#         cursor.execute(sql,val)
#         mydb.commit()
#         cursor.close()
#         return 'Done!!'


if __name__ == "__main__":
    app.run(port=6969, debug=True, host='0.0.0.0') #0.0.0.0 makes it available to all devices on the network