import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer

from socket import *
from threading import *
# import Opencv module
import numpy
import base64
import cv2

client_form_class = uic.loadUiType("./ui/client.ui")[0]
client_info_form_class = uic.loadUiType("./ui/client_info.ui")[0]

class Client_window(QWidget,client_form_class):
    # class constructor
    def __init__(self, ip, port): #main.py에서 입력한 ip를 매개변수로
        # call QWidget constructor
        super().__init__()
       
        self.setupUi(self)
        self.initialize_socket(ip, port) #소켓 초기화
        # create a timer
        self.timer = QTimer()
        # set timer timeout callback function
        self.timer.timeout.connect(self.viewCam)
        # set control_bt callback clicked  function
        self.control_bt.clicked.connect(self.controlTimer)

    def initialize_socket(self, ip, port) :
        self.client_socket = socket(AF_INET, SOCK_STREAM) #소켓 생성
        remote_ip = ip 
        remote_port = port
        self.client_socket.connect((remote_ip, remote_port))
        
    def send_video(self, socket) : #서버(호스트)로부터 요청을 받았을 때 영상을 전송해주는 함수
        try :
            while self.cap.isOpened() :
                ret, frame = self.cap.read()
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                result, imgencode = cv2.imgencode('.jpg', frame, encode_param)
                data = numpy.array(imgencode)
                stringData = base64.b64encode(data)
                length = str(len(stringData))
                self.client_socket.sendall(length.encode('utf-8').ljust(64))
                self.client_socket.send(stringData)
        
        except :
            self.client_socket.close()
    
    def send_video_thread(self) : #클라이언트 접속 후 start 버튼을 클릭했을 때 thread를 생성한다.
        # 그 후 send_video 함수를 통해 호스트(서버)로 영상을 전송될 수 있게 한다.
        send_video_th = Thread(target = self.send_video, args = (self.client_socket, ))
        send_video_th.start()
    
    # view camera
    def viewCam(self):
        # read image in BGR format
        ret, image = self.cap.read()
        # convert image to RGB format
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # get image infos
        height, width, channel = image.shape
        step = channel * width
        # create QImage from image
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        # show image in img_label
        self.image_label.setPixmap(QPixmap.fromImage(qImg))

    # start/stop timer
    def controlTimer(self):
        # if timer is stopped
        if not self.timer.isActive():
            # create video capture
            self.cap = cv2.VideoCapture(0)
            # start timer
            self.timer.start(20)
            # update control_bt text
            self.control_bt.setText("Stop")
        # if timer is started
        else:
            # stop timer
            self.timer.stop()
            # release video capture
            self.cap.release()
            # update control_bt text
            self.control_bt.setText("Start")
        
class Client_info_window(QWidget, client_info_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.commit_btn.clicked.connect(self.button_commit)
        self.show()
        
    def button_commit(self):
        self.StudentNumber = self.StudentNumber_text.text() # line_edit text 값 가져오기 
        self.StudentName = self.Name_text.text()
        
        self.hide()
        self.client_window=Client_window()
        self.client_window.StudentID_label.setText(self.StudentNumber)
        self.client_window.Name_label.setText(self.StudentName)
        self.client_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Client_info_window()
    myWindow.show()
    app.exec_()
