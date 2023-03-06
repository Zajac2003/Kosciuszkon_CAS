import PySimpleGUI as sg
import sqlite3
from functions import *

# database
db = sqlite3.connect("LIFTMATE_DATABASE.db")
cursor = db.cursor()

window = create_window("activity", activityid=0)

while True:
    event, values = window.read()

window.close()