import RPi.GPIO as GPIO
import time
pin = 12
NEUTRAL = 7.5
ZERO = 2.5
FULL = 12.5

def toDutyCycle(deg):
	return ZERO+10.0*deg/180.0

GPIO.setmode(GPIO.BOARD)

GPIO.setup(pin,GPIO.OUT)

servo = GPIO.PWM(pin,50) #50?
servo.start(NEUTRAL)

try:
    while True:
        deg = int(raw_input())
	
	servo.ChangeDutyCycle(toDutyCycle(deg))
        #time.sleep(5)
        #servo.ChangeDutyCycle(FULL)
        #time.sleep(5)
        #servo.ChangeDutyCycle(ZERO)
        #time.sleep(5)
        #print 'go power rangers'

except KeyboardInterrupt:
    GPIO.cleanup()
    print 'kill!!!!'
