import time
import mido
from rpi_ws281x import *
import random
import os
from multiprocessing import Process
import colorsys
from colorsys import hls_to_rgb, rgb_to_hls


LED_COUNT      = 288   
LED_PIN        = 18    
LED_FREQ_HZ    = 800000
LED_DMA        = 10    
LED_BRIGHTNESS = 255   
LED_INVERT     = False 
LED_CHANNEL    = 0     

class MColor:
    def __init__(self, r=0, g=0, b=0):
        self.red = int(r)
        self.green = int(g)
        self.blue = int(b)

    def getFloatList(self):
        rf = float(self.red)/255.0
        gf = float(self.green)/255.0
        bf = float(self.blue)/255.0
        return [rf,gf,bf]

    def getInt(self):
        return (65536*self.red) + (256*self.green) + self.blue
        
    def setBright(self,brightness=0.5):
        pass
    

class Strip:
    def __init__(self):
        self.leds = [MColor() for _ in range(LED_COUNT)]

    def fill(self, cc):
        for d in range(LED_COUNT):
            self.leds[d] = cc
    
    def setLedFromStrip(self, lednum, strip):
        self.leds[lednum] = strip.leds[lednum]

    def setLedFromKey(self, note, colstrip):
        skrt = int(round((float(note-21)*float(172.0/86.0))))
        bum = skrt+113
        if(bum <= 144): bum+=1
        if(bum >= 236): bum-=1
        self.leds[bum] = colstrip.leds[bum]
        self.leds[bum+1] = colstrip.leds[bum]
    
    def setLedsFromPiano(self, piano, colstrip, bgcol):
        ke = piano.keys
        for key in range(len(ke)):
            if ke[key]:
                self.setLedFromKey(key,colstrip)
            else:
                self.setLedFromKey(key,bgcol)



class Piano:
    def __init__(self):
        self.keys = [0 for _ in range(109)]

    def keyState(self, keynum):
        return bool(self.keys[keynum])

    def getColor(self, port):
        stt = 0
        sta = [0,0,0]
        stb = 0
        while(stt is not 3):
            self.updatePiano(port)
            for o in range(22,109):
                if (self.keyState(o)):
                    if (not stb):
                        if (o is not stb):
                            stb = o
                            sta[stt] = int((o-22)*(255/87))
                            stt += 1
                if ((o is stb) and (not self.keyState(stb))):
                    stb = 0
            print (sta)
        return MColor(*sta)


    def updatePiano(self, port):
        msg = port.poll()
        if msg:
            #print(msg)
            if (msg.type is "note_on"):
                self.keys[msg.note] = msg.velocity

def wheel(pos):
    if pos < 85:
        return MColor(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return MColor(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return MColor(0, pos * 3, 255 - pos * 3)

def rainbow(speed=0.3):
    n = time.time()*speed
    timex = n - float(int(n))
    j = int(timex*255)
    leds = [(wheel((i+j) % 255)) for i in range(LED_COUNT)]
    return leds

if __name__ == '__main__':
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    print(mido.get_input_names())
    port = mido.open_input(mido.get_input_names()[2])
    pressed = Strip()
    background = Strip()
    pressy = MColor(200,20,20)
    presscol = Strip()
    presscol.fill(pressy)
    #bgcolor = MColor(20,20,20)
    bgcolor = MColor(0,0,0)
    background.fill(bgcolor)
    real = Piano()
    multi = Strip()
    rain = Strip()
    stt = 0
    while True:
        rain.leds = rainbow()
        real.updatePiano(port)
        pressed.setLedsFromPiano(real, rain, background)
        for num in range(LED_COUNT):
            strip.setPixelColor(num, color=pressed.leds[num].getInt())
        
        if (real.keyState(21)):
            bgcolor = real.getColor(port)
            background.fill(bgcolor)
                        
        strip.show()


    
