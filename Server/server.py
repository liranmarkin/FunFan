import socket
import RPi.GPIO as GPIO
import numpy as np
import cv2
import os
import thread
import json
import pickle


class Servo():
    pin = None
    NEUTRAL = 7.5
    ZERO = 2.5
    FULL = 12.5
    servo = None

    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(self.pin, GPIO.OUT)

        self.servo = GPIO.PWM(self.pin, 50)  # 50?
        self.servo.start(self.NEUTRAL)

    def toDutyCycle(self, deg):
        return self.ZERO + 10.0 * deg / 180.0

    def turnTo(self, deg):
        self.servo.ChangeDutyCycle(self.toDutyCycle(deg))

    def cleanup(self):
        GPIO.cleanup()

class Camera():
    camera_port = None
    pic_width = None
    pic_height = None
    FOV = 75
    camera = None
    img_url = "./img.png"
    img1_url = "./img1.png"

    def take_picture(self):
        retval, im = self.camera.read()
        if im is None or im.shape is None:
            return
        cv2.imwrite(self.img1_url, im)
        if os.path.isfile(self.img_url):
            os.remove(self.img_url)
        os.rename(self.img1_url, self.img_url)

    def get_image(self):
        return cv2.imread(self.img_url, 0)

    def __init__(self, camera_port):
        self.camera_port = camera_port
        self.camera = cv2.VideoCapture(self.camera_port)
        self.pic_width = self.camera.get(3)
        self.pic_height = self.camera.get(4)
        if not self.camera.isOpened():
            print "Error starting camera"


    def get_camera_params(self):
        print "Camera params: " + str(self.pic_width) + " " + str(self.pic_height) + " " + str(self.FOV)
        return [self.pic_width, self.pic_height, self.FOV]




def shoot(camera):
    while True:
        camera.take_picture()

camera = None
servo = None
server = None




class Server():
    sock = None
    host = None
    port = None
    MAX_CLIENTS = 5
    def __init__(self, HOST, PORT):
        self.sock = socket.socket()
        self.host = HOST
        self.port = PORT
        self.sock.bind((HOST, PORT))
        self.sock.listen(self.MAX_CLIENTS)

    def loop(self):
        while True:
            self.conn, self.addr = self.sock.accept()
            while self.handle(self.conn):
                pass
            self.conn.close()

    def send_data(self, data):
        lengeth = len(data)
        print "sending: " + str(lengeth).ljust(16)
        self.conn.send(str(lengeth).ljust(16))
        print "sending: " + str(data)
        self.conn.sendall(data)

    def handle(self, conn):
        data = conn.recv(1024).strip()
        print data
        if data == "getImg":
            # img = camera.get_image()
            # data = np.array(img).tostring()
            ret = "hola me"
            self.send_data(ret)
            return True
            # self.request.sendall(json.dumps(img))
        elif data == "getParms":
            self.send_data(json.dumps(camera.get_camera_params()))
            return True
        else:
            try:
                deg = float(data)
                if deg < 0 or deg >= 180:
                    self.send_data("Error")
                    return False
                servo.turnTo(deg)
                self.send_data("Success")
                return True
            except:
                self.send_data("Error")
                return False


def start_server(HOST, PORT):

    # Create the server, binding to HOST:PORT
    server = Server(HOST, PORT)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.loop()

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    #start camera on channel 1
    camera = Camera(camera_port= -1)
    thread.start_new_thread(shoot, (camera, ))

    #start servo on pin 12
    servo = Servo(pin= 12)

    try:
        start_server(HOST, PORT)
    except KeyboardInterrupt:
        servo.cleanup()
