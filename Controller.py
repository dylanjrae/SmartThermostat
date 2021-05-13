import paho.mqtt.client as mqtt

from DataManager import DataManager
import mysql.connector
from datetime import datetime
import requests, json


class Controller:
        
    def __init__(self, host):
        self.host = host
        self.dataManager = DataManager()
        self.mydb = mysql.connector.connect(host='10.0.0.69',user='root',port='3306', password='pmwpmwpmw',database='tempLog')
        self.mycursor = self.mydb.cursor()
        
    def start_connection(self):
        self.client = mqtt.Client(client_id="Python_DashBoard", clean_session=True, userdata=None, transport="tcp")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        print("Attempting to connect to mqtt server...")
        self.client.connect(self.host, port=1883)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
    
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        #client.subscribe("$SYS/#")
        
        #Channels to subscribe to:
        client.subscribe("therm/main", qos=0)
        client.subscribe("therm/TEMPSET", qos=0)
        client.subscribe("therm/OVERRIDE", qos=0)
        client.subscribe("therm/CURRENTTEMP", qos=0)
        client.subscribe("therm/STATUS", qos=0)
        client.subscribe("therm/FURNACE", qos=0)
        
    
    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, message):
        message.payload = message.payload.decode("utf-8")
        
        print("Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))
        
        if message.topic == "therm/CURRENTTEMP":
            self.dataManager.currentTemps.append(float(message.payload))
            self.writeToSQL("temp", float(message.payload))
            
        if message.topic == "therm/FURNACE":
            self.dataManager.currentTemps.append(float(message.payload))
            self.writeToSQL("status", str(message.payload))
            
            #Need to record time of each temp
        elif message.topic == "therm/STATUS":
            self.dataManager.status.append(str(message.payload))

        elif message.topic == "therm/main":
            self.dataManager.mains.append(str(message.payload))

        elif message.topic == "therm/OVERRIDE":
            
            print("Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))
            
    def writeToSQL(self, table, data):
        date, time = self.getDateTime()

        if table == "temp":
            sql = "INSERT INTO Temperature_Log_Test (date, time, temperature, weatherTemp) VALUES (%s, %s, %s, %s)"
            val = (date, time, data, self.getWeatherTemp("Calgary"))
        elif table == "status":
            sql = "INSERT INTO Furnace_Log_Test (date, time, status) VALUES (%s, %s, %s)"
            val = (date, time, data)
        self.mycursor.execute(sql, val)
        self.mydb.commit()
        return 

    def getDateTime(self):
        now = datetime.now()

        date= now.strftime("%m/%d/%Y")
        print("date:",date)

        time = now.strftime("%H:%M:%S")
        print("time:",time)
        return date,time

    def getWeatherTemp(self, city):
        BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
        # CITY = "Calgary"
        API_KEY = "7b224f577fe259701d9c084236cebd6b"
        # upadting the URL
        weatherTemp = 0
        URL = BASE_URL + "q=" + city + "&appid=" + API_KEY + "&units=metric"
        # HTTP request
        response = requests.get(URL)
        # checking the status code of the request
        if response.status_code == 200:
            # getting data in the json format
            data = response.json()
            # getting the main dict block
            main = data['main']
            # getting temperature
            weatherTemp = main['temp']

            print(f"Weather Temperature: {weatherTemp}")
        else:
            # showing the error message
            print("Error in the HTTP request")
        return weatherTemp

    control = Controller("10.0.0.69")
    print("Welcome to the NutHouse Thermostat Server!")
    control.start_connection()
    control.client.loop_start()


