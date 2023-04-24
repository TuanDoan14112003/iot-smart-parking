
# import mysql.connector
# import json
# from datetime import datetime


# mydb = mysql.connector.connect(
# host="localhost",
# user="tuandoan",
# db="smart_parking_db"
# )

# mycursor = mydb.cursor()
# # while True:
# sql = f"INSERT INTO parking (id, firstName, lastName, phone, model, plate, time) VALUES (NULL,'tuan','doan','0123','toyota','SYV-23N','2016-09-06 14:00:45')"
# mycursor.execute(sql)

# mydb.commit()

# print(mycursor.rowcount, "record inserted.")

# print(mydb)







# from datetime import datetime
# now = datetime.now()
# print(now.strftime("%Y-%m-%d %H:%M:%S"))


import mysql.connector

# mydb = mysql.connector.connect(
#   host="localhost",
#   user="tuandoan",
#   database="smart_parking_db"
# )

# mycursor = mydb.cursor()

# mycursor.execute("SELECT * from parking WHERE Date(time) = '2023-04-23'")

# myresult = mycursor.fetchall()

# print(len(myresult))
import serial
import json
import threading
from datetime import datetime
device = '/dev/cu.usbmodem1201'
arduino = serial.Serial(device,9600)
import flask

app = flask.Flask("arduino project")
app.config['SECRET_KEY'] = 'secret!'

def edge():
    while True:
        print(123)
        serialData = arduino.readline()
        decodedData = serialData.decode("utf-8")
        print(decodedData)
        entry = json.loads(decodedData)    
        password = entry["password"]

        if password == "Zz38dDtS3tXwveW":
            arduino.write(b"open")


def webserver():
    app.run(threaded=True,debug=False,host='0.0.0.0',port=8080)
thread1 = threading.Thread(target=edge)
thread1.start()

thread2 = threading.Thread(target=webserver)
thread2.start()
# 