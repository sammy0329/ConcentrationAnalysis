from psutil import users
from graph import *
import db_auth as dbs
from firebase_admin import db
import time
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import socket
import random
import threading
import base64
import numpy
import cv2
from PyQt5.QtGui import QPixmap
import pickle
import struct
from _thread import *

form_class = uic.loadUiType('./ui/Widget_test.ui')[0]

client_info=[]
exlist=[]
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
clients = [] #클라이언트 리스트

class Clientclass(QThread):
    timeout = pyqtSignal(dict)    # 사용자 정의 시그널
    
    def __init__(self,classname):
        super().__init__()
        self.client_info=[]           # 초깃값 설정
        self.classname=classname 
        self.users={}

    def run(self):      
        try:
            while True:
                dbs.dir = db.reference(self.classname)
                self.db_dict = dbs.dir.get()
                self.client_info=[]
                self.log_list = []
                self.que_size = 30
                self.log_list={}
                
                for name in self.db_dict:
                    self.info_dir = db.reference(self.classname+"/"+name+"/"+"학생정보")
                    self.student_info_dic = self.info_dir.get()
                    self.users[name]=self.student_info_dic
                    print("!")
                    self.log_dir = db.reference(self.classname+"/"+name+"/"+"분석로그")
                    self.student_log = self.log_dir.get()
                    print(name, len(self.student_log))

                    if len(self.student_log)>=self.que_size:
                        for i, each in enumerate(self.student_log):
                            if len(self.student_log)-i <=self.que_size:
                                self.log_list.append(self.student_log[each])

                    else:
                        self.log_list = list(0 for i in range(self.que_size-len(self.student_log)))
                        for each in self.student_log:
                            self.log_list.append(self.student_log[each])
                    
                    print(self.log_list)
                    self.log_list=[]
                    print("="*20)

                self.timeout.emit(self.users)
        
                time.sleep(3)
        except:
            pass
            
            
  
class Host_window(QWidget, form_class):
    def __init__(self,classname):
        super().__init__()
        self.local_ip=socket.gethostbyname(hostname)
        self.setupUi(self)
        self.classname=classname
        self.cli=Clientclass(self.classname)
        self.cli.start()
        self.cli.timeout.connect(self.timeout)   # 시그널 슬롯 등록
        
        self.setupUI()
        self.show()
        
    def setupUI(self):
        self.client_table.doubleClicked.connect(self.tableWidget_doubleClicked)
        self.client_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.serverwindow = MainServer()   
        self.serverwindow.changePixmap.connect(self.setImage)
        self.serverwindow.start()
        
    def tableWidget_doubleClicked(self):
        row = self.client_table.currentIndex().row()
    
        #더블클릭시 클라이언트 이름 따오기
        client_IP = self.client_table.item(row, 4).text()
        # print(clients[0])
        # self.serverwindow.send_signal(clients[0])
        self.myGUI = CustomMainWindow()
        print(client_IP)
        for i in reversed(range(self.Graph_layout.count())):
            self.Graph_layout.removeItem(self.Graph_layout.itemAt(i))

        self.Graph_layout.addWidget(self.myGUI.myFig)
    
    @pyqtSlot(QImage)
    def setImage(self, image):
        self.image_label.setPixmap(QPixmap.fromImage(image))
        self.image_label.update()


    @pyqtSlot(dict)
    def timeout(self, users):
        
        self.client_table.setRowCount(len(users.keys()))
        self.client_table.setColumnCount(6)
        self.client_table.setColumnHidden(4, True)
        self.client_table.setColumnHidden(5, True)
        # self.client_table.resizeRowToContents(2)
        # self.client_table.resizeColumnToContents(2)
        #애초에 소팅 설정해두면 에러가 나서 끊어주고 데이터 넣고 다시 True로 바꿔줌.
        self.client_table.setSortingEnabled(False)

        for i,each in enumerate(users.keys()):
            a=random.randint(1,100)
            #집중도 숫자로 표현
            item_refresh = QTableWidgetItem()
            # item_refresh.setData(Qt.DisplayRole, int(exlist[i])) #숫자로 설정 (정렬을 위해)
            item_refresh.setData(Qt.DisplayRole, a)

            #집중도에 따른 색상 변경
            if a>60:
                item_refresh.setForeground(QBrush(QColor(50, 205, 50)))
                item_refresh.setFont(QFont("Arial", 10))
            elif a>40:
                item_refresh.setForeground(QBrush(QColor(247 , 230, 0)))
                item_refresh.setFont(QFont("Arial", 10))
            else:
                item_refresh.setForeground(QBrush(QColor(255, 0, 0)))
                # item_refresh.setFont(QFont("Times", 7, QFont.Bold))
                item_refresh.setFont(QFont("Arial", 10, QFont.Bold))

            
            self.client_table.setItem(i,0,QTableWidgetItem(users[each]['학번']))
            self.client_table.setItem(i,1,QTableWidgetItem(users[each]['이름']))
            self.client_table.setItem(i,2, item_refresh)
            self.client_table.setItem(i,4,QTableWidgetItem(users[each]['IP']))
            
        
        self.client_table.setSortingEnabled(True)

class MainServer(QThread) :
    changePixmap = pyqtSignal(QImage)
    
    def __init__(self) :
        super().__init__()
        self.s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.ip = ""
        self.ip=local_ip
        self.port = 2500 #우선 포트 번호 2500으로 고정. 나중에 수정 가능
        self.s_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #다중 접속 방지
        self.s_sock.bind((self.ip, self.port)) #ip와 port를 바인드
        print('Socket bind complete')
        self.s_sock.listen(100) #접속자 100명까지
        print('Socket now listening')
        
        self.data = b'' ### CHANGED
        self.payload_size = struct.calcsize("L") ### CHANGED



    def viewCam(self):
      
        self.student_client = self.c_socket, (self.ip, self.port) = self.s_sock.accept()

        self.conn=self.c_socket
            # if student_client not in clients :
        if self.student_client not in clients :
            clients.append(self.c_socket) #클라이언트 리스트에 클라이언트가 없다면 추가
                
            print(self.ip + " : " + str(self.port) + "가 연결되었습니다.")
            
        while True:
            # print('계속도는중')
          
            
            # self.student_client = self.c_socket, (self.ip, self.port) = self.s_sock.accept()

            # self.conn=self.c_socket
            # # if student_client not in clients :
            # if self.student_client not in clients :
            #     clients.append(self.c_socket) #클라이언트 리스트에 클라이언트가 없다면 추가
                
            # print(self.ip + " : " + str(self.port) + "가 연결되었습니다.")
         
            # Retrieve message size
            while len(self.data) < self.payload_size:
                self.data +=  self.conn.recv(4096)

            packed_msg_size = self.data[:self.payload_size]
            self.data = self.data[self.payload_size:]
            msg_size = struct.unpack("L", packed_msg_size)[0] ### CHANGED

            # Retrieve all data based on message size
            while len(self.data) < msg_size:
                self.data +=  self.conn.recv(4096)

            self.frame_data = self.data[:msg_size]
            self.data = self.data[msg_size:]

            # Extract frame
            self.frame = pickle.loads(self.frame_data)
            
          
            # read image in BGR format
            # ret, image = frame.read()
            # convert image to RGB format
         
         
        #   rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        # h, w, ch = rgb_image.shape
        # bytes_per_line = ch * w
        # convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        # return QPixmap.fromImage(p)
    
            self.image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            # get image infos
            height, width, channel = self.image.shape
            step = channel * width
            # create QImage from image
            self.qImg = QImage(self.image.data, width, height, step, QImage.Format_RGB888)
            
            # show image in img_label
            self.changePixmap.emit(self.qImg)
            # self.image_label.setPixmap(QPixmap.fromImage(qImg))

    def run(self):
        self.viewCam()
       
            # ret, frame = self.frame.read()
            # if ret:
            #     # https://stackoverflow.com/a/55468544/6622587
            #     rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #     h, w, ch = rgbImage.shape
            #     bytesPerLine = ch * w
            #     convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            #     p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            #     self.changePixmap.emit(p)
            
            # self.viewCam(self.frame)
            # print('ㅇㅇㅇ')
            # self.rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB) 
            # self.convertToQtFormat = QImage(self.rgbImage.data, self.rgbImage.shape[1], self.rgbImage.shape[0], QImage.Format_RGB888) 
            # self.pixmap = QPixmap(self.convertToQtFormat) 
            # self.p = self.pixmap.scaled(400, 225, Qt.IgnoreAspectRatio) 
            
        
            


        
    # def run(self) : #클라이언트가 접속할 때 실행되는 함수
    #     while True :
    #         student_client = c_socket, (ip, port) = self.s_sock.accept()

     
    #         # if student_client not in clients :
    #         if c_socket not in clients :
    #             clients.append(c_socket) #클라이언트 리스트에 클라이언트가 없다면 추가
                
    #         print(ip + " : " + str(port) + "가 연결되었습니다.")
    #         print(c_socket)
    #         self.show_address(c_socket,ip, port)
    
    # def show_address(self,c_socket, ip, port) : #호스트 채팅창에 ip와 port, 이름을 보여준다. 
    #     info_message = ("{} : {} 가 연결되었습니다.".format(ip, port))
    #     message_text = QTextBrowser()
    #     message_text.setPlainText(info_message)
        
        
    # def send_signal(self, socket) : #표 더블 클릭을 했을 때 클라이언트에게 시그널을 보내 영상을 요청한다.
    #     signal_message = "1"
    #     signal_message=signal_message.encode('utf-8')
    #     socket.send(signal_message)
    #     self.show_thread(socket)

    # def show_thread(self, socket) : #시그널을 보낸 후 show_thread 실행
    #     show_th = threading.Thread(target = self.show_video, args = (socket, ))
    #     show_th.start()
    
    # # view camera
    # def viewCam(self,show_image):
    #     # read image in BGR format
    #     ret, image = show_image
    #     # convert image to RGB format
    #     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #     # get image infos
    #     height, width, channel = image.shape
    #     step = channel * width
    #     # create QImage from image
    #     qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
    #     # show image in img_label
    #     self.image_label.setPixmap(QPixmap.fromImage(qImg))

    # def show_video(self, socket) : #호스트의 캔버스에 클라이언트의 영상을 보여준다.
    #     while True :
    #         try :
    #             length = self.recvall(socket, 64)
    #             receive_length = length.decode('utf-8')
    #             stringData = self.recvall(socket, int(receive_length))
    #             data = numpy.frombuffer(base64.b64decode(stringData), numpy.uint8)
    #             show_image = cv2.imdecode(data, 1)
    #             self.viewCam(show_image)
    #         except :
    #             socket.close()

    # def recvall(sock, count) : #수신받은 후 buf 반환
    #     buf = b''
    #     while count:
    #         newbuf = sock.recv(count)
    #         if not newbuf: return None
    #         buf += newbuf
    #         count -= len(newbuf)
    #     return buf


if __name__ =='__main__':
    app = QApplication(sys.argv)
    host_window = Host_window()
    host_window.show()
    app.exec_()