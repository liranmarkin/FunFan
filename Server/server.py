import SocketServer
import RPi.GPIO as GPIO
import cv2


class Servo():
    pin = 12
    NEUTRAL = 7.5
    ZERO = 2.5
    FULL = 12.5
    servo = None

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(self.pin, GPIO.OUT)

        self.servo = GPIO.PWM(self.pin, 50)  # 50?
        self.servo.start(self.NEUTRAL)

    def toDutyCycle(self, deg):
        return self.ZERO + 10.0 * deg / 180.0

    def turnTo(self, deg):
        self.servo.ChangeDutyCycle(self.toDutyCycle(deg))

class Camera():
    camera_port = 1
    pic_width = None
    pic_height = None
    FOV = 75
    camera = None
    img_url = ""

    def get_image(self):
        # read is the easiest way to get a full image out of a VideoCapture object.
        retval, im = self.camera.read()
        return im

    def save_image(self):


    def __init__(self):
        self.camera = cv2.VideoCapture(self.camera_port)
        self.pic_width = self.camera.get(3)
        self.pic_height = self.camera.get(4)

    def get_camera_params(self):
        return self.pic_width, self.pic_height, self.FOV









class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "{} wrote:".format(self.client_address[0])
        print self.data
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()