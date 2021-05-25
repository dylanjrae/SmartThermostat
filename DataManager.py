'''
Created on Feb. 20, 2021

@author: dylanrae
'''
from datetime import datetime
import mysql.connector

class DataManager():

    def __init__(self, host):
        self.currentTemps = []
        self.status = []
        self.mains = []
        self.furnaceStatus = []
        self.data = []
        self.host = host
        
        self.mydb = mysql.connector.connect(host=self.host, user='root',port='3306', password='pmwpmwpmw',database='tempLog')
        self.mycursor = self.mydb.cursor()
        
        #all messages should be stored in a df with Timestamp object
        
    
    def writeToSQL(self, table, data):
        date, time = self.getDateTime()
        if table == "thermData":
            sql = "INSERT INTO " + table + " (Date, Time, currentTemp, setTemp, heating, battery) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (date, time, data.split("/")[0], data.split("/")[1], data.split("/")[2], data.split("/")[3])
            print("Inserting: " + data.split("/")[0] + "/" + data.split("/")[1] + "/" + data.split("/")[2] + "/" + data.split("/")[3])
        
        elif table == "Schedule":
            print("Updating the schedule!")

            sql = "UPDATE " + table + "SET" + "(time, setTemperature) = (%s, %s) WHERE time = (%s)"
            #sql = "INSERT INTO " + table + " (time, setTemperature) VALUES (%s, %s)"
            for hour, setTemperature in data.items():
                dataEntry = (hour, setTemperature)
                print("Inserting: " + dataEntry[0] +"/" + dataEntry[1])

                self.mycursor.execute(sql, dataEntry, hour)
                self.mydb.commit()
            
            return


        # elif table == "temp":
        #     sql = "INSERT INTO Temperature_Log_Test (date, time, temperature, weatherTemp) VALUES (%s, %s, %s, %s)"

        #     val = (date, time, data, self.getWeatherTemp("Calgary"))
        # elif table == "status":
        #     sql = "INSERT INTO Furnace_Log_Test (date, time, status) VALUES (%s, %s, %s)"
        #     val = (date, time, data)
        
        
        
        self.mycursor.execute(sql, val)
        self.mydb.commit()

        return 
    

    
    def getDateTime(self):
        now = datetime.now()

        date= now.strftime("%Y-%m-%d")
        print("date:",date)

        time = now.strftime("%H:%M:%S")
        print("time:",time)
        return date,time
