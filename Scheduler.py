# from PySide2 import QtGui, QtCore
# import PySide2.QtWidgets as QBase
import sys

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


class DailySchedule():
    def __init__(self):
        self.temperatureDayScheduleDict = {}

        for number in range(0,24):
            timeEntry = {number : ""}
            self.temperatureDayScheduleDict.update(timeEntry)

    def setDailySchedule(self, enteredSchedule):
        pass
    
    def __repr__(self):
        dailySchedule = "The current daily schedule is:"

        for key, value in self.temperatureDayScheduleDict.items():
            dailySchedule = dailySchedule + "\n ---------------------------------------------------------"
            dailySchedule = dailySchedule + "\n Hour: " + str(key) + "\t Set Temperature: " + str(value)

        return dailySchedule



if __name__ == "__main__":
    tempScheduler = Scheduler("dataManager")

    # app = QtCore.QApplication(sys.argv)
    # window = QBase.QWidget()
    # window.setWindowTitle("Daily Temperature Scheduler")
    # layout = QBase.QVLayout()


