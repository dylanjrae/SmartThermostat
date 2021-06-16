import paho.mqtt.client as mqtt

from DataManager import DataManager
from Scheduler import Scheduler

from datetime import datetime
import requests, json
import time


class Controller: 
    def __init__(self, host):
        self.host = host
        self.dataManager = DataManager(self.host)
        self.client = None  
        # self.mydb = mysql.connector.connect(host=self.host, user='root',port='3306', password='pmwpmwpmw',database='tempLog')
        # self.mycursor = self.mydb.cursor()
        
    def startMQTTconnection(self):
        self.client = mqtt.Client(client_id="Python_BackEnd", clean_session=True, userdata=None, transport="tcp")
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
        print("Retained messages:")
        client.subscribe("therm/main", qos=0)
        client.subscribe("therm/TEMPSET", qos=0)
        client.subscribe("therm/OVERRIDE", qos=0)
        client.subscribe("therm/CURRENTTEMP", qos=0)
        client.subscribe("therm/STATUS", qos=0)
        client.subscribe("therm/FURNACE", qos=0)
        #main data channel
        client.subscribe("therm/DATA")
        
    
    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, message):
        message.payload = message.payload.decode("utf-8")
        
        print("Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))
        
        # if message.topic == "therm/CURRENTTEMP":
        #     self.dataManager.currentTemps.append(float(message.payload))
        #     # self.writeToSQL("temp", float(message.payload))
            
        # if message.topic == "therm/FURNACE":
        #     self.dataManager.currentTemps.append(float(message.payload))
        #     # self.writeToSQL("status", str(message.payload))
            
        # elif message.topic == "therm/STATUS":
        #     self.dataManager.status.append(str(message.payload))

        # elif message.topic == "therm/main":
        #     self.dataManager.mains.append(str(message.payload))

        # elif message.topic == "therm/OVERRIDE":
        #     pass
        
        # Temp way to ignore the retained message on data
        # if message.retain==1:
        #     return
        
        if message.topic == "therm/DATA":
            self.dataManager.data.append(str(message.payload))
            self.dataManager.writeToSQL("thermData", str(message.payload))
        
        # if message.topic == "therm/TEMPSET":
            
            # self.dataManager.writeToSQL("thermData", str(message.payload))           
    

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
    
    def checkSetTempChange(self):
        newTemp = self.dataManager.checkSetTempChange()
        if(newTemp):
            self.client.publish("therm/TEMPSET", str(self.dataManager.setTemp), qos=0, retain=True)
    
    
#put this in a if__main__
control = Controller("127.0.0.1")
print("Welcome to the NutHouse Thermostat Server!")
control.startMQTTconnection()
control.client.loop_forever()
# tempScheduler = Scheduler("dataManager")
# tempScheduler.setACertainHour(6, 23)
# while True:
#     # print(scheduler.get_jobs())
#     # scheduler.run_pending()
    # control.checkSetTempChange()
    # time.sleep(10)
    # check if the temp table has changed in this loop too




# Listen to db and whenever a new value there send it out
# schedule needs to write in values to a db I need to create

#compare the checksum to the old value
#if different, get most recent data value
#then publish


