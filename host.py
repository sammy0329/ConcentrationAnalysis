from graph import *
import db_auth as dbs
from firebase_admin import db
import time
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import socket
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
clients = {} #클라이언트 딕셔너리
whoosegraph=[]
users={}
class Clientclass(QThread):
    timeout = pyqtSignal(dict) # 사용자 정의 시그널
    
    def __init__(self,classname):
        super().__init__()
        self.client_info=[] # 초깃값 설정
        self.classname=classname 
        self.graph_client_log=[]
    #누구의 그래프를 받을지 이름 넘겨받음
    
    @pyqtSlot(str)
    def whosename(self, mix_info):
        self.mix_info=mix_info
        # self.graph_client_name,self.graph_client_name=mix_info.split('_')
        try:
            self.graph_client_log=users[self.mix_info]['log']
            global whoosegraph
            whoosegraph=self.graph_client_log
        except:
            pass
        
    
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
                    users[self.student_info_dic['학번']+'_'+name]={}
                    users[self.student_info_dic['학번']+'_'+name]['info']=self.student_info_dic
                    # print(self.student_info_dic['학번'])
                    
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
                    
                    users[self.student_info_dic['학번']+'_'+name]['log']=self.log_list
                
                    self.log_list=[]
                   
                    try: 
                        self.status_dir = db.reference(self.classname+"/"+name+"/"+"학생상태")
                        self.student_status=self.status_dir.get()
                        users[self.student_info_dic['학번']+'_'+name]['status']=self.student_status['status']
                    
                    except:                       
                        users[self.student_info_dic['학번']+'_'+name]['status']=''                 
                         
            except:
                pass

            self.timeout.emit(users)
            
            time.sleep(1)

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
        self.serverwindow.sendMessage.connect(self.setText)
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

    @pyqtSlot(str)
    def setText(self, text) :
        self.message_TextBrowser.setTextColor(QColor(0, 0, 0))
        self.message_TextBrowser.append(text)
        self.message_TextBrowser.update()
        
    @pyqtSlot(dict)
    def timeout(self, users):
        
        self.client_table.setRowCount(len(users.keys()))
        self.client_table.setColumnCount(6)
        self.client_table.setColumnHidden(4, True)
        self.client_table.setColumnHidden(5, True)
        self.client_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        #애초에 소팅 설정해두면 에러가 나서 끊어주고 데이터 넣고 다시 True로 바꿔줌.    
        self.client_table.setSortingEnabled(False)

        for i,each in enumerate(users.keys()):
            try:
                self.a=float(users[each]['log'][-1])
            except:
                pass
   
            #집중도 숫자로 표현
            concentration_rate=QTableWidgetItem()
            my_status=QTableWidgetItem()
          
            #집중도에 따른 색상 변경
            if self.a>0.6:
            
                concentration_rate.setData(Qt.DisplayRole, '상')
                concentration_rate.setForeground(QBrush(QColor(50, 205, 50)))
                concentration_rate.setFont(QFont("Arial", 10))
                             
            elif self.a>0.4:
                
                concentration_rate.setData(Qt.DisplayRole, '중')
                concentration_rate.setForeground(QBrush(QColor(247 , 230, 0)))
                concentration_rate.setFont(QFont("Arial", 10))
                          
            else:
               
                    
         
                concentration_rate.setData(Qt.DisplayRole, '하')
                concentration_rate.setForeground(QBrush(QColor(255, 0, 0)))

                
                student_num,student_name=each.split('_')
        
                text="학번: {} 이름: {} 집중도 주의 요망.".format(student_num,student_name)
                self.message_TextBrowser.setTextColor(QColor(255, 51, 0))
                
            
                self.message_TextBrowser.append(text)
                self.message_TextBrowser.update()
            
            if users[each]['status']=='normal':
               
                my_status.setData(Qt.DisplayRole, 'Normal')
                my_status.setForeground(QBrush(QColor(50, 205, 50)))
                my_status.setFont(QFont("Arial", 10))
            else:
               
                student_num,student_name=each.split('_')
                text="학번: {} 이름: {} 주의 산만.".format(student_num,student_name)   
                self.message_TextBrowser.setTextColor(QColor(255, 51, 0))     
                self.message_TextBrowser.append(text)
                self.message_TextBrowser.update()
                    
                    
                my_status.setData(Qt.DisplayRole, users[each]['status'])
                my_status.setForeground(QBrush(QColor(255, 0, 0)))
                my_status.setFont(QFont("Arial", 10, QFont.Bold))


            self.client_table.setItem(i,0,QTableWidgetItem(users[each]['info']['학번']))
            self.client_table.setItem(i,1,QTableWidgetItem(users[each]['info']['이름']))
            self.client_table.setItem(i,2, concentration_rate)
            self.client_table.setItem(i,3,my_status)
            self.client_table.setItem(i,4,QTableWidgetItem(users[each]['info']['IP']))
            self.client_table.item(i, 0).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.client_table.item(i, 1).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.client_table.item(i, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            self.client_table.item(i, 3).setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        
        self.client_table.setSortingEnabled(True)


class MainServer(QThread) :
    changePixmap = pyqtSignal(QImage)
    stop_image=pyqtSignal(str)
    sendMessage = pyqtSignal(str)
    
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
        text_msg = "클라이언트 ip : {} / port : {} 연결되었습니다.".format(str(addr[0]), str(addr[1])) 
        self.sendMessage.emit(text_msg)
        # 클라이언트가 접속을 끊을 때 까지 반복합니다. 
        while True: 
            #click이벤트 받으면 그 사람의 소켓번호 들고옴
            try:
                # 데이터가 수신되면 클라이언트에 다시 전송합니다.(에코)
                self.data = client_socket.recv(4096)
                # if self.data=='stop':
                #     print('Disconnected by ' + addr[0],':',addr[1])
                #     del(clients[addr[0]])
                #     print(clients)
                #     break
                
                if not self.data: 
                    print('Disconnected by ' + addr[0],':',addr[1])
                    text_msg = "클라이언트 ip : {} / port : {} 나갔습니다.".format(str(addr[0]), str(addr[1])) 
                    del(clients[addr[0]])
                    self.sendMessage.emit(text_msg)
                    break
    
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
                
          

                        
            except ConnectionResetError as e:
                
                print('Disconnected by ' + addr[0],':',addr[1])
                text_msg = "클라이언트 ip : {} / port : {} 나갔습니다.".format(str(addr[0]), str(addr[1])) 
                del(clients[addr[0]])
                self.sendMessage.emit(text_msg)
                print(clients)
                break
      
                
        client_socket.close() 

    def run(self):
        while True:
            print('wait')
            self.client_socket, self.addr = self.s_sock.accept() 
            # start_new_thread(self.threaded, (self.client_socket, self.addr))
            t = threading.Thread(target=self.threaded, args=(self.client_socket, self.addr)) 
            t.daemon = True 
            t.start()


            print(clients)
            if self.client_socket not in clients.values() :
                clients[self.addr[0]]=self.client_socket #클라이언트 딕셔너리에 클라이언트가 없다면 추가 
                print(clients)

if __name__ =='__main__':
    app = QApplication(sys.argv)
    host_window = Host_window()
    host_window.show()
    app.exec_()