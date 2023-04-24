import serial
import mysql.connector
import json
from datetime import datetime

device = '/dev/cu.usbmodem11301'
arduino = serial.Serial(device,9600)
mydb = mysql.connector.connect(
host="localhost",
user="tuandoan",
db="smart_parking_db"
)

mycursor = mydb.cursor()
while True:
    serialData = arduino.readline()
    decodedData = serialData.decode("utf-8")

    entry = json.loads(decodedData)    
    password = entry["password"]

    if password == "Zz38dDtS3tXwveW":
        arduino.write(b"open")
        firstName, lastName = entry["name"].split()
        phone = entry["phone"]
        model = entry["model"]
        plate = entry["plate"]
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = f"INSERT INTO parking (id, firstName, lastName, phone, model, plate, time) VALUES (NULL,'{firstName}','{lastName}','{phone}','{model}','{plate}','{time}')"
        mycursor.execute(sql)

        mydb.commit()

        print(mycursor.rowcount, "record inserted.")
    else:
        print("not authenticated")








