import mysql.connector
import csv

db = mysql.connector.connect(
    user='root',
    password='',
    host='192.168.2.113',
    database='obd/gps-datenlogger'
)

cursor = db.cursor()
##cursor.execute("SELECT * FROM importobd")
##firstline = True
with open('/home/pi/Schreibtisch/Studienarbeit_OBD_Datenlogger/OBD-Logger/Files/18_10_25_16_29_01_test.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(csvfile)
    for row in reader:
        print(row)
        sql = "INSERT INTO importobd (time, speed, rpm, engine_load, maf, temperature, pedal, afr, fuel_level) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, row)
        
db.commit()

##route_name = "test"
##lat = 20
##lng = 20
##
##cursor = db.cursor()
##sql = "INSERT INTO gpsdata (route_name, lat, lng) VALUES (%s, %s, %s)"
##val = (route_name, lat, lng)
##cursor.execute(sql, val)
##db.commit()

#print(cursor.lastrowid)
db.close()