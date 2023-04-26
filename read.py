import serial
import time
import schedule


def main_func():
    arduino = serial.Serial('com4', 600)
    print('Established serial connection to Arduino')
    arduino_data = arduino.readline()

    decoded_values = str(arduino_data[0:len(arduino_data)].decode("utf-8"))
    list_values = decoded_values.split('x')

    for item in list_values:
        list_in_floats.append(int(item))

    print(f'Collected readings from Arduino: {list_in_floats}')

    arduino_data = 0
    #list_in_floats.clear()
    #list_values.clear()
    arduino.close()
    print('Connection closed')
    print('<----------------------------->')


# ----------------------------------------Main Code------------------------------------
# Declare variables to be used
list_values = []
list_in_floats = []

print('Program started')
#main_func()
# Setting up the Arduino
schedule.every(1).seconds.do(main_func)

while True:
     schedule.run_pending()
     time.sleep(0.1)
























'''
import serial
import time

try:
   arduino = serial.Serial('/dev/ttyACM0', 9600)
except:
   print "Failed to connect on /dev/ttyACM0"


try:
   print arduino.readline()

   while True:
      if arduino.readline() == 'E':
        print("Detected!\n")

except:
   print ("Failed to read!")
'''