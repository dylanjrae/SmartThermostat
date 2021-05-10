import tkinter as tk


class GUIController:
    
    def __init__(self, controller):
        self.controller = controller
        
        print("Welcome to the NutHouse Thermostat Dash Board!")
        self.controller.start_connection()
       
    def mainMenu(self):
        window = tk.Tk()
        header = tk.Label(text = "Welcome to the Dashboard")
        header.pack()
        header.mainloop()
        



    
    
    
    
    