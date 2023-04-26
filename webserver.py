from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO
import mysql.connector
import json
import serial
import threading
from calendar import monthrange, month_name
from datetime import datetime, timedelta
password = None
with open("password.txt",'r') as file:
    password = file.readline().strip()




mydb = mysql.connector.connect(
host="localhost",
user="tuandoan",
database="smart_parking_db"
)
mycursor = mydb.cursor(dictionary= True)

device = '/dev/cu.usbmodem1201'
arduino = serial.Serial(device,9600)


app = Flask("arduino project")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
@app.route('/')
def index():
    entryDictionary = {}
    averagePerDay = {}
    for i in range(7):
        previousDay = datetime.now() - timedelta(days=i)
        entryQuery = f"SELECT * from Parking_Entry WHERE Date(time) = '{previousDay.strftime('%Y-%m-%d')}'"
        mycursor.execute(entryQuery)
        myresult = mycursor.fetchall()
        numberOfEntries = mycursor.rowcount
        entryDictionary.update({str(previousDay.day): str(numberOfEntries)})
    
    currentYear = datetime.now().year
    for month in range(1,13):
        lastDay = monthrange(2023, month)[1]
        totalEntresInMonthQuery = f"SELECT * from Parking_Entry WHERE time BETWEEN '{currentYear}-{month}-01' AND '{currentYear}-{month}-{lastDay}'"
        mycursor.execute(totalEntresInMonthQuery)
        mycursor.fetchall()
        averagePerDay.update({str(month_name[month]): str(mycursor.rowcount / lastDay)})
        


    customerQuery = f"SELECT * from Customer"
    mycursor.execute(customerQuery)
    customers = mycursor.fetchall()
    print(averagePerDay)
    return render_template('index.html', customerList = customers,entries = entryDictionary, averagePerDay = averagePerDay)

@app.route('/changepassword', methods=["POST"])
def changePassword():
    global password
    password = request.form.get('password')
    with open("password.txt",'w') as file:
        file.write(password) 
    return redirect("/")

@socketio.on('message')
def handle_message(data):
    if data == "open gate":
        print(data)
        arduino.write(b"open")


def edge():
    while True:
        serialData = arduino.readline()
        decodedData = serialData.decode("utf-8")
        entry = json.loads(decodedData)    
        print(entry)
        customerID = entry["customerID"]
        if entry["password"] == password:
            customerID = int(customerID,0)
            arduino.write(b"open")
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = f"INSERT INTO Parking_Entry (id, CustomerID, time) VALUES (NULL,{customerID},'{time}')"
            mycursor.execute(sql)
            mydb.commit()
            print(mycursor.rowcount, "record inserted.")
        else:
            print("not authenticated")

def startServer():
    app.run(threaded=True,debug=True,use_reloader= False,host='0.0.0.0',port=8080)

thread1 = threading.Thread(target=edge)
thread1.start()

thread2 = threading.Thread(target=startServer)
thread2.start()

