import socket
import json
import cv2
import time
import pickle


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

class PeopleDetector(object):
    def __init__(self):
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        # self.hogParams = {'winStride': (4, 4), 'padding': (32, 32), 'scale': 1.05}
        self.hogParams = {'winStride': (4, 4), 'padding': (8, 8), 'scale': 1.05}

    def get(self, img):
        foundLocations, foundWeights = self.hog.detectMultiScale(img, **self.hogParams)
        r = None
        if len(foundLocations) > 0 and len(foundLocations[0]) > 0:
            r = foundLocations[0]
            # print("Results: " + str(r))
        return r

getImg = "getImg"
getParms = "getParms"
pic_width = None
pic_height = None
FOV = None

def step(PD, sock):
    received = None
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
        sock.sendall(getImg + "\n")
        len = recvall(sock, 16)
        received = recvall(sock, len)

    except:
        print "Error connecting server"
        return

    finally:
        sock.close()

    img = None
    try:
        print received
        img = pickle.loads(received)
        #img = json.loads(received)[0]
    except:
        print "Error on getting image"
        return

    print img

    if img is None or img.shape is None:
        return

    res = PD.get(img)
    if res is not None:
        (x, y, w, h) = res
        xpos = x + w / 2.0

        #calculate deg by xpos
        deg = float(xpos)/pic_width*FOV + (90 - FOV/2.0)

        #send to server
        sock.sendall(str(deg))

        #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #cv2.imshow('image', img)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()



if __name__ == '__main__':

    HOST, PORT = 'localhost', 9999

    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, PORT))
        print "connected"

        sock.sendall(getParms + "\n")

        # Receive data from the server and shut down
        received = sock.recv(1024)

        print received

        if received == "Error":
            print "error on getting params"
            exit()
        [pic_width, pic_height, FOV] = json.loads(received)

    except:
        print "Cannot connect to server"
        exit()

    finally:
        sock.close()

    PD = PeopleDetector()


    while True:
        step(PD, sock)
        time.sleep(1)

