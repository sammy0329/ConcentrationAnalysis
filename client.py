import sys
import time
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QThread
import numpy as np
import db_auth as dbs
from firebase_admin import db
import cv2
from socket import *
import pickle
import struct
from sub_model import sub_model
from requests import get
import torch
from model.models.resmasking import resmasking50_dropout1
from torchvision.transforms import transforms
import torch.nn.functional as F
from PyQt5.QtCore import QCoreApplication

client_form_class = uic.loadUiType("./ui/client.ui")[0]
client_info_form_class = uic.loadUiType("./ui/client_info.ui")[0]

prdeict_list = ['분노', '역겨움', '공포', '행복', '슬픔', '놀람', '무표정']
weight_list = [0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 1]

model_path = "C:/res_model.pt"
seg_model = torch.load(model_path)
seg_model.eval()

hostname = gethostname()
# local_ip= gethostbyname(hostname)
local_ip=get('https://api.ipify.org').text

transform = transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.ToTensor(),
            ]
)

def classifier(frame_input):
    frame_input = cv2.resize(frame_input, (224, 224), interpolation=cv2.INTER_LINEAR)
    frame_input = cv2.cvtColor(frame_input, cv2.COLOR_BGR2GRAY)
    frame_input = np.array(frame_input)
    frame_input = np.dstack([frame_input] * 3)
    frame_input = transform(frame_input)
    frame_input = frame_input.reshape(1,3,224,224)
    # frame_input.to(torch.device('cuda'))
    result = seg_model(frame_input)
    result = F.softmax(result, dim=1)
    result = result.tolist()[0]

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
                result_list = classifier(frame)
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
        bg_img = QImage("ui/img/client.jpg")
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(bg_img))
        self.setPalette(palette)
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
        
    def closeEvent(self):
        QMessageBox.question(self, 'Message', 'Host가 회의를 종료했습니다.',
                                     QMessageBox.Yes , QMessageBox.Yes)

    def send_video(self) : #서버(호스트)로부터 요청을 받았을 때 영상을 전송해주는 함수
        try:
            while True:
                # self.server_socket, self.addr = self.soc.accept()
                    
                ret,frame=self.cap.read()
                    # Serialize frame
                retval, frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])    
                frame = pickle.dumps(frame)
                self.soc.sendall(struct.pack(">L", len(frame)) + frame)
                # print("보내는중")
                
        except ConnectionResetError as e:
            self.soc.close()
            #QtWidgets.QMessageBox.critical(self, "QMessageBox", "QMessageBox Error")
            QCoreApplication.quit()
            
    def run(self):    
        self.soc = socket(AF_INET, SOCK_STREAM)

        host = self.ip # 서버 아이피
        port = 2500 # 서버 포트
        self.myip=local_ip
        self.soc.connect( (host, port) ) # 서버측으로 연결한다.
        print("연결 성공")

        self.send_video()

class Client_info_window(QWidget, client_info_form_class):
    def __init__(self, dir_name, server_ip):
        super().__init__()
        self.client_ip=local_ip
        self.dir_name = dir_name
        self.server_ip = server_ip
        self.setupUi(self)

        bg_img = QImage("ui/img/client_info2.jpg")
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(bg_img))
        self.setPalette(palette)

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
        print(self.SutdentIP)
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