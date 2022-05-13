# from psutil import users
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
clients = {} #클라이언트 리스트
whoosegraph=[]
class Clientclass(QThread):
    timeout = pyqtSignal(dict) # 사용자 정의 시그널
    
    def __init__(self,classname):
        super().__init__()
        self.client_info=[] # 초깃값 설정
        self.classname=classname 
        self.users={}
        self.graph_client_log=[]
    #누구의 그래프를 받을지 이름 넘겨받음
    
    @pyqtSlot(str)
    def whosename(self, mix_info):
        self.mix_info=mix_info
        self.graph_client_name,self.graph_client_name=mix_info.split('_')
        self.graph_client_log=self.users[self.graph_client_name]['log']
        global whoosegraph
        whoosegraph=self.graph_client_log
        
    
    def run(self):      
        while True:
            dbs.dir = db.reference(self.classname)
            self.db_dict = dbs.dir.get()
            self.client_info=[]
            self.log_list = []
            self.que_size = 200
            self.log_list={}
            try:
                i = 0
                for name in self.db_dict:
                    
                    i+=1
                    self.info_dir = db.reference(self.classname+"/"+name+"/"+"학생정보")
                    self.student_info_dic = self.info_dir.get()
                    self.users[name]={}
                    self.users[name]['info']=self.student_info_dic
                    
                    self.log_dir = db.reference(self.classname+"/"+name+"/"+"분석로그")
                    self.student_log = self.log_dir.get()
                    if self.student_log is None:
                        self.student_log={}

                    if len(self.student_log)>=self.que_size:
                        for i, each in enumerate(self.student_log):
                            if len(self.student_log)-i <=self.que_size:
                                self.log_list.append(self.student_log[each])

                    else:
                        self.log_list = list(0 for i in range(self.que_size-len(self.student_log)))
                        for each in self.student_log:
                            self.log_list.append(self.student_log[each])
                    
                    self.users[name]['log']=self.log_list
                
                    self.log_list=[]
            except:
                pass

            self.timeout.emit(self.users)
            
            time.sleep(3)

class Host_window(QWidget, form_class):
    whose_graph = pyqtSignal(str)
    cam_signal=pyqtSignal(str)
    def __init__(self,classname):
        super().__init__()
        self.local_ip=socket.gethostbyname(hostname)
        self.setupUi(self)
        self.classname=classname
        self.cli=Clientclass(self.classname)
        self.cli.start()
        self.cli.timeout.connect(self.timeout) # 시그널 슬롯 등록
        self.whose_graph.connect(self.cli.whosename)
        self.setupUI()
        self.show()
        
    def setupUI(self):
        self.client_table.doubleClicked.connect(self.tableWidget_doubleClicked)
        self.client_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.serverwindow = MainServer()
        self.cam_signal.connect(self.serverwindow.click_event) # 시그널 연결
        self.serverwindow.changePixmap.connect(self.setImage)
        self.serverwindow.start()
        
    def tableWidget_doubleClicked(self):
        row = self.client_table.currentIndex().row()
    
        # 더블클릭시 클라이언트 이름 따오기
        client_IP = self.client_table.item(row, 4).text()
        self.client_num = self.client_table.item(row, 0).text()
        self.client_name= self.client_table.item(row, 1).text()
        self.client_mix=self.client_num+'_'+self.client_name
        self.cam_signal.emit(client_IP) # ip를 signal로 넘김
        self.whose_graph.emit(self.client_mix)
        
        # my_list=[]
        # for i in range(100):
        #     my_list.append(i)
       
        self.myGUI = CustomMainWindow()
        self.myGUI.addData_callbackFunc(whoosegraph)
       
        
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

            self.client_table.setItem(i,0,QTableWidgetItem(users[each]['info']['학번']))
            self.client_table.setItem(i,1,QTableWidgetItem(users[each]['info']['이름']))
            self.client_table.setItem(i,2, item_refresh)
            self.client_table.setItem(i,4,QTableWidgetItem(users[each]['info']['IP']))
            
        
        self.client_table.setSortingEnabled(True)


class MainServer(QThread) :
    changePixmap = pyqtSignal(QImage)
    
    def __init__(self) :
        super().__init__()
        self.s_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.ip = ""
        self.ip=local_ip
        self.port = 2500 #우선 포트 번호 2500으로 고정. 나중에 수정 가능
        # self.s_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #다중 접속 방지
        self.s_sock.bind((self.ip, self.port)) #ip와 port를 바인드
        print('Socket bind complete')
        self.s_sock.listen(100) #접속자 100명까지
        print('Socket now listening')
        
        self.data = b'' ### CHANGED
        self.payload_size = struct.calcsize("L") ### CHANGED
        self.clicked_ip=''

    #click이벤트에서 값 받아옴
    @pyqtSlot(str)
    def click_event(self,clicked_ip):
        self.clicked_ip=clicked_ip
        
    # 쓰레드에서 실행되는 코드입니다. 
    # 접속한 클라이언트마다 새로운 쓰레드가 생성되어 통신을 하게 됩니다. 
    def threaded(self,client_socket, addr): 

        print('Connected by :', addr[0], ':', addr[1]) 

        # 클라이언트가 접속을 끊을 때 까지 반복합니다. 
        while True: 
            #click이벤트 받으면 그 사람의 소켓번호 들고옴
            try:
                if self.clicked_ip: 
                    if clients[self.clicked_ip]==client_socket:
                        msg='Yes'
                        client_socket.send(msg.encode())
                        # 데이터가 수신되면 클라이언트에 다시 전송합니다.(에코)
                        self.data = client_socket.recv(4096)
                        
                        # Retrieve message size
                        while len(self.data) < self.payload_size:
                            self.data +=  self.client_socket.recv(4096)

                        packed_msg_size = self.data[:self.payload_size]
                        self.data = self.data[self.payload_size:]
                        msg_size = struct.unpack("L", packed_msg_size)[0] ### CHANGED

                        # Retrieve all data based on message size
                        while len(self.data) < msg_size:
                            self.data +=  self.client_socket.recv(4096)

                        self.frame_data = self.data[:msg_size]
                        self.data = self.data[msg_size:]

                        # Extract frame
                        self.frame = pickle.loads(self.frame_data)

                
                        self.image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                        # get image infos
                        height, width, channel = self.image.shape
                        step = channel * width
                        # create QImage from image
                        self.qImg = QImage(self.image.data, width, height, step, QImage.Format_RGB888)
                        
                        # show image in img_label
                        self.changePixmap.emit(self.qImg)
                       
                    else:
                        msg='No'
                        client_socket.send(msg.encode())


            except ConnectionResetError as e:

                print('Disconnected by ' + addr[0],':',addr[1])
                del(clients[addr[0]])
                print(clients)
                break
                
        client_socket.close() 

    def run(self):
        while True:
            print('wait')
            self.client_socket, self.addr = self.s_sock.accept() 
            start_new_thread(self.threaded, (self.client_socket, self.addr))
            
            if self.client_socket not in clients.values() :
                clients[self.addr[0]]=self.client_socket #클라이언트 딕셔너리에 클라이언트가 없다면 추가 
                print(clients)

if __name__ =='__main__':
    app = QApplication(sys.argv)
    host_window = Host_window()
    host_window.show()
    app.exec_()