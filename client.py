import sys
import cv2
import time
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QThread
import tensorflow as tf
import numpy as np
import db_auth as dbs
from firebase_admin import db
import base64
import cv2
from socket import *
from threading import *

client_form_class = uic.loadUiType("./ui/client.ui")[0]
client_info_form_class = uic.loadUiType("./ui/client_info.ui")[0]

prdeict_list = ["놀람", "슬픔", "무표정", "행복", "공포", "역겨움", "분노"]
weight_list = [0.1, 0.1, 1, 0.2, 0.1, 0.1, 0.1]

model_path = "C:/test_model.h5"
seg_model = tf.keras.models.load_model(model_path)

def classifier(frame_input):
    frame_input = cv2.resize(frame_input, (256, 256), interpolation=cv2.INTER_LINEAR)
    frame_input = np.array(frame_input)
    result = seg_model.predict(np.array([frame_input]))

    return result

class Analysis_upload(QThread):
    def __init__(self, cv_cap):
        super().__init__()
        self.cap = cv_cap
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_counter = 0

    def run(self):
        while True:
            ret, frame = self.cap.read()
            self.frame_counter += 1

            if not ret:
                break

            if self.frame_counter % self.fps == 0:
                result_vector = classifier(frame)
                # result = prdeict_class[np.argmax(result_vector)]
                result_list = result_vector.reshape(-1)
                concent_rate = 0

                for i, each in enumerate(result_list):
                    concent_rate += each * weight_list[i]
                    print(i, each, weight_list[i], each * weight_list[i], sep="\t")
                print("sum = ", concent_rate * 100)
                print("*" * 20)

                time_now = time.localtime(time.time())
                time_now = time.strftime("%H:%M:%S", time_now)

                query = "{{'{}':'{}'}}".format(time_now, concent_rate)
                query = eval(query)
                # dbs.dir.update(query)
                print(query)

class Client_window(QWidget,client_form_class):
    # class constructor
    def __init__(self, ip, port):
        # call QWidget constructor
        super().__init__()
       
        self.setupUi(self)
        self.cap = cv2.VideoCapture(0)
        self.anl = Analysis_upload(self.cap)
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

    def receive_signal(self, socket) : #시그널을 받았을 때 send_video 호출하는 함수
        while True :
            buf = socket.recv(256)
            print(buf.decode('utf-8'))
            self.send_video(socket)

    def send_video(self, socket) : #서버(호스트)로부터 요청을 받았을 때 영상을 전송해주는 함수
        try :
            while self.cap.isOpened() :
                ret, frame = self.cap.read()
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                result, imgencode = cv2.imgencode('.jpg', frame, encode_param)
                data = np.array(imgencode)
                stringData = base64.b64encode(data)
                length = str(len(stringData))
                self.client_socket.sendall(length.encode('utf-8').ljust(64))
                self.client_socket.send(stringData)
        
        except :
            self.client_socket.close()

    def send_video_thread(self) : #클라이언트 소켓 생성시 발생하는 스레드
        send_video_th = Thread(target = self.receive_signal, args = (self.client_socket, ))
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
            self.anl.start()
            # start timer/
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
        self.student_id = self.StudentName
        self.class_name = "컴퓨터 네트워크"
        self.time_now = time.localtime(time.time())
        self.time_now = time.strftime("%D일%H시", self.time_now)
        self.directory = self.student_id + "/" + self.class_name
        dbs.dir = db.reference(self.directory)
        
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
