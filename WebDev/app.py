from flask import Flask, render_template, jsonify #, url_for, request, redirect
#from flask_sqlalchemy import SQLAlchemy
#from flask_mysqldb import MySQL
import mysql.connector
# import datetime
import json
import requests




app = Flask(__name__)


#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#mydb = mysql.connector.connect(host='10.0.0.69',user='root',, password='pmwpmwpmw',database='tempLog')
#mycursor = self.mydb.cursor()
#app.config['MYSQL_HOST'] = '10.0.0.69'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'pmwpmwpmw'
#app.config['MYSQL_DB'] = 'flask'
#app.config['MYSQL_PORT'] = '3306'

#mysql = MySQL(app)




@app.route('/')
def index():

    return render_template('index.html')

@app.route('/api/currentStatus', methods=['GET'])
def currentStatus():
        # get the most recent data record
    sql = "SELECT * FROM `thermData` ORDER BY `thermData`.`Date` DESC, `thermData`.`Time` DESC LIMIT 1"
    
    myDb = mysql.connector.connect(host='10.0.0.69',user='root',port='3306', password='pmwpmwpmw',database='tempLog')
    cursor = myDb.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()

    if result[0][4] == 1:
        furnaceStatus = "ON"
    else:
        furnaceStatus = "OFF"

    date = result[0][0].strftime("%b %-d, %Y")
    time = str(result[0][1])
    
    statusSet = {"setTemp" : result[0][3], "upstairsTemp" : result[0][2], "downstairsTemp" : "coming soon!", "furnaceStatus" : furnaceStatus, "date" : date, "time": time}
    return jsonify(statusSet)



if __name__ == "__main__":
    app.run(port=6969, debug=True, host='0.0.0.0') #0.0.0.0 makes it available to all devices on the network

