import serial
import tkinter as tk
import time
import schedule

# Declare variables to be used
list_values = []
arduinoReadings = []
n = 0  # number of hall call
NS = 0 # number of known stops
callButton = [0, 0, 0, 0, 0, 0]  # storing hall calls

#dyncHallCall() = 0  # hall call (it is constant)
NF = 4  # number of floors
TF = 2  # Trip Floor Time in second
PT = 3  # Passive Time second

arduino = serial.Serial('com4', 750)
print('Established serial connection to Arduino')

def dyncHallCall():
    for i in range(0,6):
        if callButton[i] == 1:
            if i==0:
                return 1
            elif i== 1 or i==3:
                return 2
            elif i==2 or i==4:
                return 3
            elif i==5:
                return 4

def direction():
    # print("In direction")
    arduinoRead()
    for k in arduinoReadings:
        if k == 1:
            return 1
        elif k == 0:
            return 0


def hallCall():
    # print("in callButton")
    arduinoRead()
    global n  # number of hall call
    # print("TEST hallcall()")
    for i in arduinoReadings:
        i = int(i)
        if 1018 <= i <= 1023:  # 1st floor UP
            callButton[0] = 1
        elif 1002 <= i <= 1009:  # 2nd floor UP
            callButton[1] = 1
        elif 988 <= i <= 998:  # 2nd floor DOWN
            callButton[3] = 1
        elif 975 <= i <= 982:  # 3rd floor UP
            callButton[2] = 1
        elif 950 <= i <= 965:  # 3rd floor DOWN
            callButton[4] = 1
        elif 860 <= i <= 875:  # 4th floor DOWN
            # data.insert(5, 1)
            callButton[5] = 1
    #print(callButton)
    for j in callButton:
        if j == 1:
            n += 1
    #print(n)


def floorSensor(): #returns current floor
    #print("in reed-sort/ floor sensor data")
    global n
    arduinoRead()
    for i in arduinoReadings:
        i = int(i)
        if 930 <= i <= 935:  # 4th floor
            callButton[5] = 0
            if n<0:
                print("On floor : 4")
                return 4
            n -= 1
            print("On floor : 4")
            return 4
        elif 890 <= i <= 900:  # 3rd floor
            if direction() == 1:
                callButton[2] = 0
                if n < 0:
                    print("On floor : 3")
                    return 3
                n -= 1
            elif direction() == 0:
                callButton[4] = 0
                if n < 0:
                    print("On floor : 3")
                    return 3
                n -= 1
            print("On floor : 3")
            return 3
        elif 845 <= i <= 850:  # 2nd floor
            if direction() == 1:
                callButton[1] = 0
                if n < 0:
                    print("On floor : 2")
                    return 2
                n -= 1
            elif direction() == 0:
                callButton[3] = 0
                if n < 0:
                    print("On floor : 2")
                    return 2
                n -= 1
            print("On floor : 2")
            return 2
        elif 780 <= i <= 790:  # 1st floor
            callButton[0] = 0
            if n < 0:
                print("On floor : 1")
                return 1
            n -= 1
            print("On floor : 1")
            return 1


def stops():
    global NS  # number of known stops
    #print("in stop")
    hc=dyncHallCall()
    CF = floorSensor() # CF = current floor
    if hc==1:
        if direction()==0:
            for i in range(3,CF+1):
                if callButton[i]==1:
                    NS+=1
    elif hc==2:
        if direction()==1:
            pass
        elif direction()==0:
            for i in range(3,CF+1):
                if callButton[i]==1:
                    NS+=1
    elif hc==4:
        if direction()==1:
            for i in range(CF,3):
                if callButton[i]==1:
                    NS+=1
    elif hc == 3:
        if direction() == 1:
            if callButton[1]==1:
                NS+=1
        elif direction() == 0:
            pass


    # for i in range(CF, 6):
    #     if callButton[i] == 1:
    #         NS = NS + 1
    print("Stops ",NS)
    return NS

'''
def close():
    arduino.close()
    print('Connection closed')
    print('<----------------------------->')
'''

def arduinoRead():
    # arduino = serial.Serial('com4', 600)
    test = 0
    arduinoReadings.clear()

    while test != 20:
        # print('Established serial connection to Arduino')
        arduino_data = arduino.readline()

        decoded_values = str(arduino_data[0:len(arduino_data)].decode("utf-8"))
        list_values = decoded_values.split('x')

        try:
            for item in list_values:
                arduinoReadings.append(int(item))
        except ValueError:
            arduinoRead()

        test += 1

        ##print(f'Collected arduinoReadings from Arduino: {arduinoReadings}')

        arduino_data = 0

# ----------------------------------------Driver Code------------------------------------
while True:
    #print("Elevator Idle")
    hallCall()
    #schedule.every(1).seconds.do(hallCall)
    while n >= 0:
        #hallCall()
        #print(n)
        #print(callButton)
        while floorSensor() != dyncHallCall():
            #print(callButton)
            #hallCall()  #TESTING NEEDED
            if direction() == 1:  # When going UP
                if dyncHallCall() == 4:
                    #print(callButton)
                    #print("dynchc value ",dyncHallCall())
                    time = (2 * NF - 4 - floorSensor()) * TF + stops() * PT
                    print('Your elevator Waiting time for reaching 4th floor is :: {} sec '.format(time))

                elif dyncHallCall() == 3:
                    if callButton[2] == 1 and floorSensor() <= 3:
                        time = (3 - floorSensor()) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 3rd floor is :: {} sec '.format(time))
                    elif callButton[4] == 1:
                        time = (2 * NF - 3 - floorSensor()) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 3rd floor is :: {} sec '.format(time))
                    elif callButton[2] == 1 and floorSensor() > 3:
                        time = (2 * NF - floorSensor() + 3 - 2) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 3rd floor is :: {} sec '.format(time))

                elif dyncHallCall() == 2:
                    if callButton[1] == 1 and floorSensor() <= 2:
                        time = (2 - floorSensor()) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 2nd floor is :: {} sec '.format(time))
                    elif callButton[3] == 1:
                        time = (2 * NF - 2 - floorSensor()) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 2nd floor is :: {} sec '.format(time))
                    elif callButton[1] == 1 and floorSensor() > 2:
                        time = (2 * NF - floorSensor() + 2 - 2) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 2nd floor is :: {} sec '.format(time))

                elif dyncHallCall() == 1:
                    if callButton[0] == 1 and floorSensor() <= 1:
                        time = (1 - floorSensor()) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 1st floor is :: {} sec '.format(time))
                    elif callButton[0] == 1 and floorSensor() > 1:
                        time = (2 * NF - floorSensor() + 1 - 2) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 1st floor is :: {} sec '.format(time))


            elif direction() == 0:  # When going DOWN

                if dyncHallCall() == 1:
                    time = (1 + floorSensor() - 2) * TF + stops() * PT
                    print('Your elevator Waiting time for reaching 1st floor is :: {} sec '.format(time))

                elif dyncHallCall() == 3:
                    if callButton[4] == 1 and floorSensor() >= 3:  # UP call
                        time = (floorSensor() - 3) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 3rd floor is :: {} sec '.format(time))
                    elif callButton[2] == 1:
                        time = (3 + floorSensor() - 2) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 3rd floor is :: {} sec '.format(time))
                    elif callButton[4] == 1 and floorSensor() < 3:
                        time = (2 * NF + floorSensor() - 3 - 2) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 3rd floor is :: {} sec '.format(time))

                elif dyncHallCall() == 2:
                    if callButton[3] == 1 and floorSensor() >= 2:  # UP call
                        time = (floorSensor() - 2) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 2nd floor is :: {} sec '.format(time))
                    elif callButton[1] == 1:
                        time = (2 + floorSensor() - 2) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 2nd floor is :: {} sec '.format(time))
                    elif callButton[3] == 1 and floorSensor() < 2:
                        time = (2 * NF + floorSensor() - 2 - 2) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 2nd floor is :: {} sec '.format(time))

                if dyncHallCall() == 4:
                    if callButton[5] == 1 and floorSensor() >= 4:
                        time = (floorSensor() - 4) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 4th floor is :: {} sec '.format(time))
                    elif callButton[5] == 1 and floorSensor() < 4:
                        time = (2 * NF + floorSensor() - 4 - 2) * TF + stops() * PT
                        print('Your elevator Waiting time for reaching 4th floor is :: {} sec '.format(time))

