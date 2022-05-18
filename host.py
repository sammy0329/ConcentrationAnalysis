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
import cv2
from PyQt5.QtGui import QPixmap
import pickle
import struct
from _thread import *

form_class = uic.loadUiType('./ui/host.ui')[0]

client_info=[]
exlist=[]
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
clients = {} #클라이언트 리스트
whoosegraph=[]
global select_client_ip
select_client_ip = "main"
changePixmap = pyqtSignal(QImage)
global user_dict
user_dict = {"main":0}


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
        global select_client_ip
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
        #self.cam_signal.connect(self.serverwindow.click_event) #시그널 연결
        self.serverwindow.stop_image.connect(self.stop_listen)
        self.serverwindow.changePixmap.connect(self.setImage)
        self.serverwindow.start()
        
    def tableWidget_doubleClicked(self):
        global select_client_ip

        row = self.client_table.currentIndex().row()
    
        # 더블클릭시 클라이언트 이름 따오기
        client_IP = self.client_table.item(row, 4).text()
        select_client_ip = client_IP
        print(select_client_ip)
        self.client_num = self.client_table.item(row, 0).text()
        self.client_name= self.client_table.item(row, 1).text()
        self.client_mix=self.client_num+'_'+self.client_name
        #self.cam_signal.emit(client_IP) # ip를 signal로 넘김
        self.image_label.clear()
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
    

    @pyqtSlot(str)##없음
    def stop_listen(self,str_stop):
        self.str_stop=str_stop
        if self.str_stop=="stop":
                self.image_label.clear()


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
    stop_image = pyqtSignal(str)
    changePixmap = pyqtSignal(QImage)
    def __init__(self) :

        super().__init__()
        global select_client_ip
        global user_dict
        self.id_num = 1
        self.ip = local_ip
        self.port = 2500 #우선 포트 번호 2500으로 고정. 나중에 수정 가능
        
        self.key = 1
        self.num = 0

        self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        # self.s_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #다중 접속 방지
        self.server_socket.bind((self.ip, self.port)) #ip와 port를 바인드
        print('Socket bind complete')
        self.server_socket.listen(100) #접속자 100명까지
        print('Socket now listening')

    
    # 쓰레드에서 실행되는 코드입니다. 
    # 접속한 클라이언트마다 새로운 쓰레드가 생성되어 통신을 하게 됩니다. 
    def run(self):
        global user_dict
        while True:

            client_socket, address = self.server_socket.accept()
            print('클라이언트 ip 주소 :', address[0],"연결 되었습니다.")
            print("클라이언트 id ",str(self.id_num),'을 부여합니다.')
            user_dict[address[0]] = self.id_num
            client_th = threading.Thread(target = self.receive_data,args= (client_socket, self.id_num))
            client_th.start()
            self.id_num += 1
            
            print(user_dict[address[0]])

            #print("시발")
    #클라이언트 쓰레드 생성
    def receive_data(self, client_socket,id_num):
        key2 = 1
        data_buffer = b""# calcsize : 데이터의 크기(byte)
        data_size = struct.calcsize("L") ### CHANGED# - L : 부호없는 긴 정수(unsigned long) 4 bytes

        while True:
            while len(data_buffer) < data_size:
                # 데이터 수신
             
                data_buffer += client_socket.recv(4096)
      
            packed_data_size = data_buffer[:data_size]
            data_buffer = data_buffer[data_size:]
            frame_size = struct.unpack(">L", packed_data_size)[0]
        
            while len(data_buffer) < frame_size:
            
                data_buffer += client_socket.recv(4096)
            # 프레임 데이터 분할


            key2 = -1
            frame_data = data_buffer[:frame_size]
            data_buffer = data_buffer[frame_size:]
            frame = pickle.loads(frame_data)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
            height, width, channel = image.shape
            step = channel * width
            
            qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
            if(user_dict[select_client_ip] == id_num) :

                print(str(id_num)+'과 연결 되었습니다.')    
                self.changePixmap.emit(qImg)
            else:
                    if(key2 != 1):
                        self.reboot(client_socket,id_num)
                        break

    def reboot(self,socket2,id_num2):
        th = threading.Thread(target = self.receive_data,args= (socket2,id_num2))
        th.start()

if __name__ =='__main__':
    app = QApplication(sys.argv)
    host_window = Host_window()
    host_window.show()
    app.exec_()