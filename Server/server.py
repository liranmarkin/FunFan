import SocketServer
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

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def send_data(self, data):
        lengeth = len(data)
        print "sending: " + str(lengeth).ljust(16)
        self.request.send(str(lengeth).ljust(16))
        print "sending: " + str(data)
        self.request.sendall(data)

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        if self.data == "getImg":
            #img = camera.get_image()
            #data = np.array(img).tostring()
            data = "hola taylor"
            self.send_data(data)
            #self.request.sendall(json.dumps(img))
        elif self.data == "getParms":
            self.send_data(json.dumps(camera.get_camera_params()))
        else:
            try:
                deg = float(self.data)
                if deg < 0 or deg >= 180:
                    self.send_data("Error")
                    return
                servo.turnTo(deg)
                self.send_data("Success")
            except:
                self.send_data("Error")


def start_server(HOST, PORT):

    # Create the server, binding to HOST:PORT
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    #start camera on channel 1
    camera = Camera(-1)
    thread.start_new_thread(shoot, (camera, ))

    #start servo on pin 12
    servo = Servo(12)


    start_server(HOST, PORT)

    servo.cleanup()

