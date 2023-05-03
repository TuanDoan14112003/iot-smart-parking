from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO  # WebSocket library
import mysql.connector  # MySQL library to connect to the database
import json  # To deserialize the data sent by the Arduino
import serial  # PySerial library for Serial communication
import threading
from calendar import monthrange, month_name
from datetime import datetime, timedelta

password = None
with open("password.txt", 'r') as file:
    password = file.readline().strip()  # reading the local password

# Connecting to the data base
mydb = mysql.connector.connect(
    host="localhost",
    user="tuandoan",
    database="iot_project"
)
mycursor = mydb.cursor(dictionary=True)
device = '/dev/cu.usbmodem1301'
arduino = serial.Serial(device, 9600)  # Setup the Serial communication


app = Flask("arduino project")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/')
def index():
    entryDictionary = {}
    averagePerDay = {}

    for i in range(7):
        # calculate the number of entries in the last 7 days
        previousDay = datetime.now() - timedelta(days=i)
        entryQuery = f"SELECT * from Parking_Entry WHERE Date(time) = '{previousDay.strftime('%Y-%m-%d')}'"
        mycursor.execute(entryQuery)
        myresult = mycursor.fetchall()
        numberOfEntries = mycursor.rowcount
        entryDictionary.update({str(previousDay.day): str(numberOfEntries)})

    currentYear = datetime.now().year
    for month in range(1, 13):
        # calculate the average entries per day
        lastDay = monthrange(2023, month)[1]
        totalEntresInMonthQuery = f"SELECT * from Parking_Entry WHERE time BETWEEN '{currentYear}-{month}-01' AND '{currentYear}-{month}-{lastDay}'"
        mycursor.execute(totalEntresInMonthQuery)
        mycursor.fetchall()
        averagePerDay.update(
            {str(month_name[month]): str(mycursor.rowcount / lastDay)})

    customerQuery = f"SELECT * from Customer"
    mycursor.execute(customerQuery)
    customers = mycursor.fetchall()

    # find the customer with the highest number of entries
    bestCustomerQuery = f"SELECT * FROM customer WHERE numberOfEntries = ( SELECT MAX(numberOfEntries) FROM customer ) LIMIT 1;"
    mycursor.execute(bestCustomerQuery)
    bestCustomers = mycursor.fetchall()
    print(bestCustomers)
    return render_template('index.html', customerList=customers, entries=entryDictionary, averagePerDay=averagePerDay, bestCustomer=bestCustomers[0])


@app.route('/changepassword', methods=["POST"])
def changePassword():
    # change the locally stored password
    global password
    password = request.form.get('password')
    with open("password.txt", 'w') as file:
        file.write(password)
    return redirect("/")


@socketio.on('message')
def handle_message(data):
    # command the Arduino to open the gate
    if data == "open gate":
        print(data)
        arduino.write(b"open")


def edge():
    # read from the serial line to detect data from the Arduino
    while True:
        serialData = arduino.readline()
        decodedData = serialData.decode("utf-8")
        entry = json.loads(decodedData)
        print(entry)
        customerID = entry["customerID"]
        # check the password on the Mifare card against the locally stored password
        if entry["password"] == password:
            customerID = int(customerID, 0)
            # update the numberOfEntries column
            updateEntriesQuery = f"UPDATE customer SET numberOfEntries = numberOfEntries + 1 WHERE CustomerID ={customerID}"
            mycursor.execute(updateEntriesQuery)
            mydb.commit()
            arduino.write(b"open")
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = f"INSERT INTO Parking_Entry (id, CustomerID, time) VALUES (NULL,{customerID},'{time}')"
            mycursor.execute(sql)
            mydb.commit()
            print(mycursor.rowcount, "record inserted.")
        else:
            print("not authenticated")


def startServer():
    app.run(threaded=True, debug=True, use_reloader=False,
            host='0.0.0.0', port=8080)  # run the web application


thread1 = threading.Thread(target=edge)
thread1.start()

thread2 = threading.Thread(target=startServer)
thread2.start()
