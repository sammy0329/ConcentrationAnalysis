import sys
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
import cv2
from socket import *
import pickle
import struct
from sub_model import sub_model
import threading
from requests import get


client_form_class = uic.loadUiType("./ui/client.ui")[0]
client_info_form_class = uic.loadUiType("./ui/client_info.ui")[0]

prdeict_list = ["놀람", "슬픔", "무표정", "행복", "공포", "역겨움", "분노"]
weight_list = [0.1, 0.1, 1, 0.2, 0.1, 0.1, 0.1]

model_path = "C:/test_model.h5"
seg_model = tf.keras.models.load_model(model_path)
'''
model_path = "C:/model.pt"
seg_model = models.__dict__["resmasking_dropout1"]
seg_model.load_state_dict(torch.load(model_path))
print(seg_model.summary())
'''
hostname = gethostname()
local_ip=get('https://api.ipify.org').text

def classifier(frame_input):
    frame_input = cv2.resize(frame_input, (256, 256), interpolation=cv2.INTER_LINEAR)
    frame_input = np.array(frame_input)
    result = seg_model.predict(np.array([frame_input]))

    return result

class Analysis_upload(QThread):
    def __init__(self, cv_cap, base_dir):
        super().__init__()
        self.cap = cv_cap
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_counter = 0
        self.base_dir = base_dir + "/분석로그"

    def run(self):
        while True:
            ret, frame = self.cap.read()
            self.frame_counter += 1

            if not ret:
                break

            if self.frame_counter % self.fps == 0:
                result_vector = classifier(frame)
                result_list = result_vector.reshape(-1)
                concent_rate = 0

                for i, each in enumerate(result_list):
                    concent_rate += each * weight_list[i]

                time_now = time.localtime(time.time())
                time_now = time.strftime("%H:%M:%S", time_now)

                query = "{{'{}':'{}'}}".format(time_now, concent_rate)
                query = eval(query)
                dbs.dir = db.reference(self.base_dir)
                dbs.dir.update(query)
        

class Client_window(QWidget,client_form_class):
    # class constructor
    def __init__(self,server_ip, base_dir):
        # call QWidget constructor
        super().__init__()
        self.server_ip=server_ip
        self.setupUi(self)
        self.cap = cv2.VideoCapture(0)
        
        self.anl = Analysis_upload(self.cap, base_dir)
        self.submodel=sub_model(self.cap, base_dir)
        self.send=SendVideo(self.cap,self.server_ip)
        # create a timer
        self.timer = QTimer()
        # set timer timeout callback function
        self.timer.timeout.connect(self.viewCam)
        self.controlTimer()

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

    def controlTimer(self):
        # if timer is stopped
        if not self.timer.isActive():
            self.anl.start()
            self.submodel.start()
            self.send.start()
            # start timer/
            self.timer.start(20)
    

class SendVideo(QThread):

    def __init__(self, cv_cap, server_ip):
        super().__init__()
        self.cap = cv_cap
        self.ip=server_ip

    def send_video(self) : #서버(호스트)로부터 요청을 받았을 때 영상을 전송해주는 함수
        while True:
            # self.server_socket, self.addr = self.soc.accept()
            reReady = self.soc.recv(1024)
            reReady=reReady.decode()
            if reReady == "Yes":
                
                ret,frame=self.cap.read()
                # Serialize frame
                self.data = pickle.dumps(frame)

                # Send message length first
                self.message_size = struct.pack("L", len(self.data)) ### CHANGED

                # Then data
                self.soc.sendall(self.message_size + self.data)
            elif reReady=="No":
                return
           

    def run(self):    
        self.soc = socket(AF_INET, SOCK_STREAM)

        host = self.ip # 서버 아이피
        port = 2500 # 서버 포트
        self.myip=local_ip
        self.soc.connect( (host, port) ) # 서버측으로 연결한다.
      
        # print (soc.recv(1024)) # 서버측에서 보낸 데이터 1024 버퍼만큼 받는다.
        self.send_video()

        # self.soc.send("Client. Hello!!!") # 서버측으로 문자열을 보낸다.
        # self.soc.close() # 연결 종료

class Client_info_window(QWidget, client_info_form_class):
    def __init__(self, dir_name, server_ip):
        super().__init__()
        self.client_ip=local_ip
        self.dir_name = dir_name
        self.server_ip = server_ip
        self.setupUi(self)
        self.commit_btn.clicked.connect(self.button_commit)
        self.show()
        
    def button_commit(self): 
        self.StudentNumber = self.StudentNumber_text.text() # line_edit text 값 가져오기 
        self.StudentName = self.Name_text.text()
        self.SutdentIP = self.client_ip # IP 변수로 수정해야함
        self.StudentPort = 5717 # 포트 변수로 수정해야함
        
        self.directory = self.dir_name  + "/" + self.StudentName + "/학생정보"
        dbs.dir = db.reference(self.directory)

        self.query = "{{'{}':'{}'}}".format("학번", self.StudentNumber)
        self.query = eval(self.query)
        dbs.dir.update(self.query)
        
        self.query = "{{'{}':'{}'}}".format("이름", self.StudentName)
        self.query = eval(self.query)
        dbs.dir.update(self.query)
        
        self.query = "{{'{}':'{}'}}".format("IP", self.SutdentIP)
        self.query = eval(self.query)
        dbs.dir.update(self.query)

        self.query = "{{'{}':'{}'}}".format("Port", self.StudentPort)
        self.query = eval(self.query)
        dbs.dir.update(self.query)

        self.directory_base= self.dir_name  + "/" + self.StudentName
        
        self.hide()
        self.client_window=Client_window(self.server_ip, self.directory_base)
        self.client_window.StudentID_label.setText(self.StudentNumber)
        self.client_window.Name_label.setText(self.StudentName)
        self.client_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Client_info_window()
    myWindow.show()
    app.exec_()