'''
Created on Feb. 20, 2021

@author: dylanrae
'''

class DataManager:

    def __init__(self):
        self.currentTemps = []
        self.status = []
        self.mains = []
        self.furnaceStatus = []
        
        #all messages should be stored in a df with Timestamp object
        
    
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
        
