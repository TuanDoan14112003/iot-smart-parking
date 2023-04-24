from distutils.log import debug
from socket import socket
from flask import Flask, render_template
from flask_socketio import SocketIO
import mysql.connector

# import serial
from datetime import datetime, timedelta
# device = '/dev/cu.usbmodem11301'

# arduino = serial.Serial(device,9600)

app = Flask("arduino project")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
@app.route('/')
def index():
    entryDictionary = {}
    currentDay = datetime.now().day
    mydb = mysql.connector.connect(
    host="localhost",
    user="tuandoan",
    database="smart_parking_db"
    )
    mycursor = mydb.cursor()
    now = datetime.now()
    for i in range(7):
        previousDay = datetime.now() - timedelta(days=i)
        query = f"SELECT * from parking WHERE Date(time) = '{previousDay.strftime('%Y-%m-%d')}'"
        # p
        mycursor.execute(query)
        myresult = mycursor.fetchall()
        numberOfEntries = mycursor.rowcount
        entryDictionary.update({previousDay.day: numberOfEntries})
    print(entryDictionary)
    return render_template('index.html', entryDictionary)


@socketio.on('message')
def handle_message(data):
    if data == "open gate":
        arduino.write(b"open")


socketio.run(app,debug=True,host='0.0.0.0',port=8080)