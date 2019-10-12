

import pygame as pg
import pygame.midi as midi
import pyautogui
import threading


# classes
class midiController:
    def __init__(self):
        self.pads = []
        list.append(self.pads, key(48))
        list.append(self.pads, key(49))
        list.append(self.pads, key(50))
        list.append(self.pads, key(51))

        # channel 2: keys
        self.keys = []
        for i in range(0,25):
            self.keys.append(key(48+i)) # note number

        self.axisXY = []
        self.axisXY.append(axis(225, "x", 0))
        self.axisXY.append(axis(177, "y", -1))


class key:
    def __init__(self, noteNumber):
        self.state = 0
        self.oldstate = 0
        self.noteNumber = noteNumber
        self.noteVelocity = 0

class axis:
    def __init__(self, _id, name, centerValue):
        self.name = name
        self.value = 0
        self.centerValue = centerValue
        self.id = _id


mpk2mini = midiController()  # global

keyMap = ['shift',0,'a','w','s','d',0,'space',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]


def mapKeys():
    pass




def pollMidi():
    deviceCount = pg.midi.get_count()
    #print(deviceCount)
    for i in range(0, deviceCount):
        print(pg.midi.get_device_info(i))

    midi_in = pg.midi.Input(1)  # id = 1
    

    while True:
        if midi_in.poll():
            midiData = midi_in.read(1)
            #print(midiData)
            identifier = midiData[0][0][0]

            if identifier == 144:  # note on channel 1 (pads)
                for i in range(0, len(mpk2mini.pads)):
                    if midiData[0][0][1] == mpk2mini.pads[i].noteNumber:
                        mpk2mini.pads[i].state = 1

            elif identifier == 128:  # note off channel 1
                for i in range(0, len(mpk2mini.pads)):
                    if midiData[0][0][1] == mpk2mini.pads[i].noteNumber:
                        mpk2mini.pads[i].state = 0

            elif identifier == 145:  # note on channel 2 (keys)
                for i in range(0, len(mpk2mini.keys)):
                    if midiData[0][0][1] == mpk2mini.keys[i].noteNumber:
                        mpk2mini.keys[i].oldstate = mpk2mini.keys[i].state
                        mpk2mini.keys[i].state = 1
                        
            elif identifier == 129:  # note off channel 2
                for i in range(0, len(mpk2mini.keys)):
                    if midiData[0][0][1] == mpk2mini.keys[i].noteNumber:
                        mpk2mini.keys[i].oldstate = mpk2mini.keys[i].state
                        mpk2mini.keys[i].state = 0

            elif identifier == 225:  # joystick x
                mpk2mini.axisXY[0].value =  midiData[0][0][2] - 64
            elif identifier == 177:  # joystick y
                mpk2mini.axisXY[1].value =  64 - midiData[0][0][2]


            text = ""
            for i in range(0, len(mpk2mini.keys)):
                text = text + str(mpk2mini.keys[i].state)
            #print(text)

            
# TODO: multiple keys pressed -> set only last key??? key held down?? no reapeat?
# https://stackoverflow.com/questions/48682388/pyautogui-press-key-for-x-seconds
def updateKeys():
    while True:
        for i in range(0, len(mpk2mini.keys)):
            if mpk2mini.keys[i].state != mpk2mini.keys[i].oldstate:  # state changed
                if keyMap[i] != 0:
                    if mpk2mini.keys[i].state == 1:
                        pyautogui.keyDown(keyMap[i])
                    else:
                        pyautogui.keyUp(keyMap[i])

        x = mpk2mini.axisXY[0].value
        y = mpk2mini.axisXY[1].value
        print(str(x), ' ', str(y))

        xMov = 0
        yMov = 0
        
        xScale = 0.2
        yScale = xScale

        if x != mpk2mini.axisXY[0].centerValue:
            xMov = x * xScale
        if y != mpk2mini.axisXY[1].centerValue:
            yMov = y * yScale
        pyautogui.move(xMov, yMov)

        


def initAll():
    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = True
    mapKeys()

    pg.init()
    pg.midi.init()

    if pg.midi.get_init(): 
        print("success")
    else: print( "NO SUCCESS")
    


def controlFunction():
    btnState = 0  #  static, button state of last loop
    try:
        while True:
                #while(midi_in.poll()):
                #    midi_in.read(1000)  # flush buffer

                text = ""
                for i in range(0, len(mpk2mini.pads)):
                    text = text + str(mpk2mini.pads[i].state)
                print(text)

                if mpk2mini.pads[2].state == 0:
                    btnState = 0
                elif mpk2mini.pads[2].state == 1 and btnState == 0:
                    btnState = 1
                    if mpk2mini.counter == 0:
                        pyautogui.press('r')  # record
                        pg.time.wait(500)
                        mpk2mini.counter = mpk2mini.counter + 1
                    elif mpk2mini.counter == 1:
                        pyautogui.press('space')  # stop recording
                        pg.time.wait(300)
                        pyautogui.hotkey('shift', 'space') # replay
                        pg.time.wait(200)
                        mpk2mini.counter = mpk2mini.counter + 1
                    elif mpk2mini.counter == 2:
                        pyautogui.press('space')  # stop recording
                        pg.time.wait(300)
                        pyautogui.press('y') # delete
                        mpk2mini.counter = 0
                        pg.time.wait(200)
                if mpk2mini.pads[0].state == 1:  # stop
                    pyautogui.press('space')  # stop recording
                    pg.time.wait(500)


    except KeyboardInterrupt:
        print("\nkeyboard interrupt")

        


if __name__ == "__main__":
    initAll()

    pollThread = threading.Thread(target=pollMidi)
    pollThread.start()

    keysThread = threading.Thread(target=updateKeys)
    keysThread.start()

    