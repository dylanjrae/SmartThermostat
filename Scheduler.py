# from PySide2 import QtGui, QtCore
# import PySide2.QtWidgets as QBase
import schedule
import sys
import time

class Scheduler():
    """
    Will create the daily schedule object and interface with the SQL database.

    First create the dailyschedule object
    Second from maybe a signal have it send over the new daily schedule everytime it is entered on the website
    Third save this daily schedule into the SQL database

    """

    def __init__(self, dataManager):
        self.dataManager = dataManager
        self.dailySchedule = DailySchedule()
        self.fetchCurrentDaySchedule()

    def fetchCurrentDaySchedule(self):
        dailySchedule = self.dailySchedule.__repr__()
        print(dailySchedule)

    def updateTempDailySchedule(self):
        self.dataManager("Schedule", self.dailySchedule.temperatureDayScheduleDict)

    def createScheduler(self):
        schedule.clear()
        for hour, setTemperature in self.dailySchedule.temperatureDayScheduleDict.items():
            if setTemperature != "":
                militaryTime = str(hour) + ":" +"00"
                schedule.every().day.at(militaryTime).do(self.startHeating())

    def setACertainHour(self, hour, temperature):
        self.dailySchedule.temperatureDayScheduleDict[hour] = temperature
        self.fetchCurrentDaySchedule()
        return

    def startHeating(self):
        print("Run functions to turn on the furnace!")

class DailySchedule():
    def __init__(self):
        self.temperatureDayScheduleDict = {}

        for number in range(0,24):
            timeEntry = {number : ""}
            self.temperatureDayScheduleDict.update(timeEntry)

    def setDailySchedule(self, enteredSchedule):
        self.temperatureDayScheduleDict = enteredSchedule
    
    def __repr__(self):
        dailySchedule = "The current daily schedule is:"

        for key, value in self.temperatureDayScheduleDict.items():
            dailySchedule = dailySchedule + "\n ---------------------------------------------------------"
            dailySchedule = dailySchedule + "\n Hour: " + str(key) + "\t Set Temperature: " + str(value)

        return dailySchedule



if __name__ == "__main__":
    tempScheduler = Scheduler("dataManager")
    tempScheduler.setACertainHour(6, 23)

    while True:
        schedule.run_pending()
        time.sleep(10)


    # app = QtCore.QApplication(sys.argv)
    # window = QBase.QWidget()
    # window.setWindowTitle("Daily Temperature Scheduler")
    # layout = QBase.QVLayout()
