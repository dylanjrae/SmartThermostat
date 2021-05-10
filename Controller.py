import paho.mqtt.client as mqtt

from DataManager import DataManager


class Controller:
    def __init__(self, host):
        self.host = host
        self.dataManager = DataManager()
        
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
        
    
    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, message):
        message.payload = message.payload.decode("utf-8")
        
        print("Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))
        
        if message.topic == "therm/CURRENTTEMP":
            self.dataManager.currentTemps.append(float(message.payload))
            writeToSQL("tempReadings", float(message.payload))
            
            #Need to record time of each temp
        elif message.topic == "therm/STATUS":
            self.dataManager.status.append(str(message.payload))

        elif message.topic == "therm/main":
            self.dataManager.mains.append(str(message.payload))
            
        elif message.topic == "therm/OVERRIDE":
            self.dataManager.override.append((str(message.payload)))
            
            print("Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))
            
    def writeToSQL(table, data):
        #this function takes a table name and saves the data and the current date and time into the table
        
        #when a controller is made a cursor should be set up that connects and points to the sql database
        #then use that cursor in this function as the writing location
        #will likely need pyodbc(to connect to SQL server), and JinjaSQL or some sort of sql library,
        #and will poboably need a date/time library to get current time
        

control = Controller("10.0.0.69")
print("Welcome to the NutHouse Thermostat Server!")
control.start_connection()
control.client.loop_forever()


