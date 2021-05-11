from flask import Flask
from DataManager import DataManager
from Controller import Controller

app = Flask(__name__)
#control = Controller("10.0.0.69");

@app.route("/")
def index():
    
    return str(control.dataManager.currentTemps)

if __name__ == "__main__":
    control = Controller("10.0.0.69")
    print("Welcome to the NutHouse Thermostat Server!")
    control.start_connection()
    control.client.loop_start()
    app.run(host="10.0.0.69", port=6969, debug=True)
    
