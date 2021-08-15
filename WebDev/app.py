
from os import name
from flask import Flask, render_template, url_for, jsonify, request, redirect, flash #, url_for, request, redirect
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
# from flask_mysqldb import MySQL #FOR SOMEREASON THIS CAN'T WORK IN A FUNCTION WITH A MQTT DECORATOR
import mysql.connector
from flask_mqtt import Mqtt

from datetime import datetime
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
# from Scheduler import Scheduler


app = Flask(__name__)
app.config.from_object('config.ProdConfig')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
# mysqlDb = MySQL(app)
mqtt = Mqtt(app)
mqtt.subscribe("therm/DATA")

# schd = Scheduler()
# schd.setACertainHour(6, 23)






# TO DO
#  1. DONE Integrate mqtt controller with flask
#     Organize based on this guide: https://exploreflask.com/en/latest/organizing.html
#  2. Add scheduler functionality Aidan made (should be stored in database not a dict)
#  3. DONE Add set temperature functionality to webpage
#  4. Apply css and bootstrap formating
#  5. Graphs of temperature over time with outside weather data
#  6. Should have users for API/database login
#  7. Add google home functionality (what is temp and set temp)
#  8. Clean up css code and all files in general

# Get socket working for test
# then try and see if it works on apache to trrouble shoot
@app.route('/')
def index():
    # flash('Welcome!')
    return render_template('index.html')

@app.route('/schedule')
def schedule():
    return render_template('schedule.html')

@app.route('/api-details')
def apiDetails():
    return render_template('api-details.html')

@app.route('/api/currentStatus', methods=['GET'])
def currentStatus():
    # Connecting to db and getting most recent record
    sql = "SELECT * FROM `thermData` ORDER BY `thermData`.`Date` DESC, `thermData`.`Time` DESC LIMIT 1"

    myDb = mysql.connector.connect(host=app.config['MYSQL_HOST'],user=app.config['MYSQL_USER'],port=app.config['MYSQL_PORT'], password=app.config['MYSQL_PASSWORD'],database=app.config['MYSQL_DB'])
    cursor = myDb.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()

    # Formatting some of the data for return
    if result[0][4] == 1:
        furnaceStatus = "ON"
    else:
        furnaceStatus = "OFF"
    date = result[0][0].strftime("%b %-d, %Y")
    time = str(result[0][1])
    
    # The data to be returned as a JSON object
    statusSet = {"setTemp" : result[0][3], "upstairsTemp" : result[0][2], "downstairsTemp" : "coming soon!", "furnaceStatus" : furnaceStatus, "date" : date, "time": time}
    return jsonify(statusSet)

@app.route('/api/setTemp', methods=['POST'])
def setTemp():
    #default user is root, but in future will be diferent (ie Guest, djohnjames, etc.)
    userID = app.config['MYSQL_USER']
    # Get new temperature from form that was sent
    newTemp = request.form["newSetTemp"]

    #Next need to send out this temp on a retained mqtt, then write the record into the database for later viewing
    mqtt.publish('therm/TEMPSET', str(newTemp), qos=0, retain=True)
    # The sql and params
    sql = "INSERT INTO setTempLog (Date, Time, UserId, setTemp) VALUES (%s, %s, %s, %s)"
    val = (datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), userID, newTemp)

    # Connecting to db and inserting new data
    myDb = mysql.connector.connect(host=app.config['MYSQL_HOST'],user=app.config['MYSQL_USER'],port=app.config['MYSQL_PORT'], password=app.config['MYSQL_PASSWORD'],database=app.config['MYSQL_DB'])
    cursor = myDb.cursor()
    cursor.execute(sql, val)
    myDb.commit()
    cursor.close()
    
    # cur=mysqlDb.connection.cursor()
    # cur.execute(sql, val)
    # mysqlDb.connection.commit()
    # cur.close()
    return 'Success!'


# startDateTime --> starting date and time for temp data in the format YYYY-MM-DD HH:MM:SS
# endDateTime --> starting date and time for temp data in the format YYYY-MM-DD HH:MM:SS
# intervals --> number of intervals to average the data over
# returns averaged temps for number of points specified from past (0) to present (intervals-1)

# Should enforce paramter name/type
@app.route('/api/historicalTemp', methods=['GET'])
def historicalTemp():
    # recevies time stamps for desired interval
    # recieves number of periods to divide into
    
    args = request.args
    # print(args)
    
    dateTimeStart = args["startDateTime"]
    dateTimeEnd = args["endDateTime"]
    intervalCount = int(args["intervals"])
    
    sql = "SELECT thermData.Date, thermData.Time, thermData.currentTemp FROM thermData WHERE TIMESTAMP(thermData.Date, thermData.Time) >= '" +dateTimeStart+ "' AND TIMESTAMP(`Date`, `Time`) <= '" + dateTimeEnd + "' ORDER BY thermData.Date DESC, thermData.Time DESC"

    myDb = mysql.connector.connect(host=app.config['MYSQL_HOST'],user=app.config['MYSQL_USER'],port=app.config['MYSQL_PORT'], password=app.config['MYSQL_PASSWORD'],database=app.config['MYSQL_DB'])
    cursor = myDb.cursor()
    cursor.execute(sql)
    df = pd.DataFrame(cursor.fetchall())
    cursor.close()
    
    # adding a new column called datetime that combines date and time columns
    df[0] = pd.to_datetime(df[0])
    df['dateTime'] = df[0] + df[1]
    
    # calculate total time difference btween both datetimes
    difference = datetime.fromisoformat(dateTimeEnd) - datetime.fromisoformat(dateTimeStart)
    # divide this difference by the interval count
    intervalSize = difference/intervalCount
    # add this difference to datetime start and average all temp values within this range
    result = {}
    lowerBound = datetime.fromisoformat(dateTimeStart)
    upperBound = lowerBound + intervalSize
    
    for i in range(0, intervalCount):
        dfInterval = df.loc[(df['dateTime'] >= lowerBound) & (df['dateTime'] < upperBound), 2]
        samplePointCount = dfInterval.shape[0]
        if(samplePointCount == 0):
            # Should come up with something better to do if it is 0
            aveTemp = 21.69
        else:
            aveTemp = dfInterval.mean()
        result[i] = (aveTemp, samplePointCount)
        lowerBound = upperBound
        upperBound = upperBound + intervalSize
    # print(result)
    
    return jsonify(result)

    # Last 1 hour of temp date query
    # select * from thermData where TIMESTAMP(`Date`, `Time`) >= date_sub(now(),interval 1 hour) ORDER BY `Date` DESC, `Time` DESC

class User(db.Model, UserMixin):
    __tablename__ = 'accounts'
    
    # def __init__(self, id, email, name, password):
    #     self.id = id
    #     self.email = email
    #     self.name = name
    #     self.password = password
    
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(50))
    password_hash = db.Column(db.String(255))
    
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<ID: {}, Name: {}, Email: {}>'.format(self.id, self.name, self.email)
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    # submit = SubmitField('Sign In')

# Something to do with alchemy pulling from the wrong table name
# accounts = User.query.filter_by(id=1).first()
# print(accounts)

# u = User(email='dylan.rae@eecol.com', name='DOG')
# u.set_password('dawg')
# db.session.add(u)
# db.session.commit()
# print(generate_password_hash('test'))

# Need to make a form on site to test, and redirect to index if it works
@app.route('/login', methods=['GET', 'POST'])
def login_post():
    if current_user.is_authenticated:
        print("User already logged in!")
        flash("You are already logged in!")
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    print("Email: {}, Password: {}, Remember: {}", form.email.data, form.password.data, form.remember_me.data)
    # if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    print(user)
    if user is None or not user.check_password(form.password.data):
        print("here!")
        flash('Invalid email or password!')
        # return redirect(url_for('index'))
        return redirect('/')
    
    login_user(user, remember = form.remember_me.data)
    flash('Login Successful!')
    return redirect(url_for('index'))
    # return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully!')
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe("therm/DATA") #FOR SOME REASON THIS IS NOT BEING EXECUTED, probably a problem with the shit flask mqtt
    print("Connected with result code "+str(rc))
    

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    # return
    message.payload = message.payload.decode("utf-8")
    # print("Received message '" + str(message.payload) + "' on topic '"
    #     + message.topic + "' with QoS " + str(message.qos))
    if message.topic == "therm/DATA":
        # The sql and params
        sql = "INSERT INTO thermData (Date, Time, currentTemp, setTemp, heating, battery) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), message.payload.split("/")[0], message.payload.split("/")[1], message.payload.split("/")[2], message.payload.split("/")[3])
        print("Inserting: " + message.payload.split("/")[0] + "/" + message.payload.split("/")[1] + "/" + message.payload.split("/")[2] + "/" + message.payload.split("/")[3])

        # Connecting to db and inserting new data
        myDb = mysql.connector.connect(host=app.config['MYSQL_HOST'],user=app.config['MYSQL_USER'],port=app.config['MYSQL_PORT'], password=app.config['MYSQL_PASSWORD'],database=app.config['MYSQL_DB'])
        cursor = myDb.cursor()
        # sql = "INSERT INTO thermData (Date, Time, currentTemp, setTemp, heating, battery) VALUES (%s, %s, %s, %s, %s, %s)"
        # val = (datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), 69.69, 69.69, 69.69, 69.69)
        cursor.execute(sql, val)
        myDb.commit()
        cursor.close()



if __name__ == "__main__":
    app.run(port=6969, host='0.0.0.0') #0.0.0.0 makes it available to all devices on the network

