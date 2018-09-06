#!/usr/bin/env python3
# NeoPixel and MQTT light functions for Raspberry Pi
# Author: Michael Tate
# Credit to Tony DiCola for his strandtest example in the NeoPixel library
#

import time
from neopixel import *
import argparse
import random
import paho.mqtt.client as mqtt

# LED strip configuration:
LED_COUNT      = 288      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

MQTT_SERVER = "192.168.65.117"
MQTT_PATH = "kitchen_lights"

mypayload = "N/A"
breakpayload = ""
temppayload = ""

#generic color of "fire" for the candle animation. Using a float to make the randomizations smoother.
FIRE_COLOR = [125.0,210.0,15.0,0]



def createcandlecolors(): #This creates the random candle colors
    global FIRE_COLOR

    newcandlecolors = list(FIRE_COLOR)

    s = random.randint(0,80) - 40
    t = random.randint(30,80)

    newcandlecolors[0] = newcandlecolors[0] + s
    newcandlecolors[1] = newcandlecolors[1] + s/2
    newcandlecolors[2] = newcandlecolors[2] + s//3
    newcandlecolors[3] = t

    return newcandlecolors

def createcandle_bright(): #This creates the random candle brightnesses

    newcandle_bright = [1.0,0,0.0]

    s = random.randint(20,255)
    t = random.randint(5,15)

    newcandle_bright[0] = s/255.0
    newcandle_bright[1] = t
    newcandle_bright[2] = 0


    return newcandle_bright

def candle(strip):
    global mypayload
    global breakpayload
    global FIRE_COLOR
    global LED_COUNT

    LIGHT_SIZE = 4
    LIGHT_SPACING = 20
    LIGHTS = (LED_COUNT)//(LIGHT_SIZE + LIGHT_SPACING)

    candles = [list(FIRE_COLOR) for i in range(0,LIGHTS,1)]
    candles_bright = [[1.0,0,0.0] for i in range(0,LIGHTS,1)]
    newtarget = list(candles)
    newtarget_bright = list(candles_bright)
    deltacolor = [[0,0,0] for i in range(0,LIGHTS,1)]


    for x in range(0, 20000000, 1):
        for i in range(0, LIGHTS, 1):


            if candles[i][3] == 0:
                newtarget[i] = createcandlecolors()
                candles[i][3] = newtarget[i][3]
                for j in range (0, 3, 1):
                    deltacolor[i][j] = (newtarget[i][j] - candles[i][j])/candles[i][3]
                #print (deltacolor[i])
            else:
                for j in range (0, 3, 1):
                    candles[i][j] = candles[i][j] + deltacolor[i][j]
                candles[i][3] = candles[i][3] - 1


            if candles_bright[i][1] == 0:
                newtarget_bright[i] = createcandle_bright()
                candles_bright[i][1] = newtarget_bright[i][1]
                candles_bright[i][2] = (newtarget_bright[i][0] - candles_bright[i][0])/(candles_bright[i][1]*2)
            else:
                candles_bright[i][0] = candles_bright[i][0] + candles_bright[i][2]
                candles_bright[i][1] = candles_bright[i][1] - 1


        for y in range(0, LIGHTS, 1):
            for z in range(0, LIGHT_SIZE, 1):
                strip.setPixelColorRGB(y*(LIGHT_SIZE + LIGHT_SPACING) + z, int(round((candles[y][0])*candles_bright[y][0])), int(round((candles[y][1]*candles_bright[y][0]))), int(round((candles[y][2]*candles_bright[y][0]))))
        strip.show()
	if (mypayload == "turn_off") or (breakpayload == "turn_off"):
            break
        time.sleep(0.005)




def on_message(client, userdata, message):
    global mypayload
    global temppayload
    global breakpayload
    temppayload = mypayload
    print("received message = " + str(message.payload.decode("utf-8")))
    mypayload = message.payload
    breakpayload = "turn_off"

def on_connect(client, userdata, flags, rc):
    print("Connected with RC " + str(rc))
    client.subscribe(MQTT_PATH)


def packer(strip):
    global mypayload
    global temppayload
    """Draw the Packer Chase Lights"""
    s = 4 #this is the speed of the effect
    for x in range(0, 1550):
        y = 0
        while y < LED_COUNT:
            for z in range(0, 49):
                strip.setPixelColorRGB(((x+y+z) % LED_COUNT)+1,173,49,38)
            for w in range(0, 49):
                strip.setPixelColorRGB(((x+y+w+16) % LED_COUNT)+1,184,255,28)
            #print(str(((x+y+z)) % LED_COUNT) + " " + str(y))
            time.sleep(100/1000)
            y = y + 100

        strip.show()
	if mypayload == "turn_off":
	    temppayload = mypayload
            break



# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=10):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)
	global mypayload
        mypayload = "N/A"

# Define functions which animate LEDs in various ways.
def quickWipe(strip):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    global mypayload
    global breakpayload
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
	if (mypayload == "turn_off") or (breakpayload == "turn_off"):
	    break
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(MQTT_SERVER, 1883, 60)

        client.loop_start()

        while True:
   	    if mypayload == "packer_on":
       	        quickWipe(strip)
		packer(strip)
		mypayload = temppayload
		breakpayload = ""
   	    if mypayload == "rainbow":
       	        quickWipe(strip)
		rainbow(strip)
		breakpayload = ""
   	    if mypayload == "turn_off":
       	        colorWipe(strip, Color(0,0,0), 10)
		breakpayload = ""
            if mypayload == "candle":
                quickWipe(strip)
		candle(strip)
		breakpayload = ""

    except KeyboardInterrupt:
        colorWipe(strip, Color(0,0,0), 10)
        client.loop_stop()
