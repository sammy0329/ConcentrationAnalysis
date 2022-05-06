import time
import firebase_admin
from firebase_admin import credentials, db
#----------------------------------------
import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
# import PyQt5.QtWidgets as qtwid
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
#----------------------------------------
# import test23.client as client
from socket import *
from threading import *
import base64

from scipy import rand
from graph import *
import random
import cv2

# form_class = uic.loadUiType('./ui/test1.ui')[0]
# form_class = uic.loadUiType('./ui/test_graph.ui')[0]
form_class = uic.loadUiType('./ui/Widget_test.ui')[0]

key_path = "test-db-b261c-firebase-adminsdk-ddkpv-ff4ed08001.json"
db_url = "https://test-db-b261c-default-rtdb.firebaseio.com/"
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {'databaseURL' : db_url})
dir = db.reference()
client_info=[]
# exlist=[80,90,100,70,60,50,40,60,65,55,75,84,55,43,78]
exlist=[]
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
clients = [] #클라이언트 리스트
sockets = [] #소켓 리스트

class Clientclass(QThread):
    timeout = pyqtSignal(list)    # 사용자 정의 시그널
    
    def __init__(self):
        super().__init__()
        self.client_info=[]           # 초깃값 설정
        
    def run(self):      
        while True:
            self.ref = db.reference()
            self.db_dict = self.ref.get()
            self.client_info=[]
            for i, each in enumerate(self.db_dict):
                self.client_info.append(each)
            self.timeout.emit(self.client_info)
            
            time.sleep(3)
      
# class Host_window(QMainWindow, form_class):  
class Host_window(QWidget, form_class):
    def __init__(self):
        super().__init__()
       
        self.setupUi(self)
        self.cli=Clientclass()
        self.cli.start()
        self.cli.timeout.connect(self.timeout)   # 시그널 슬롯 등록
        self.setupUI()
        self.IP_label.setText(local_ip)
        self.show()
    
        #print(local_ip)
        
    def setupUI(self):
        self.client_table.doubleClicked.connect(self.tableWidget_doubleClicked)
        #표 수정 불가능하도록 만듦
        self.client_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.ipconnect_btn.clicked.connect(self.chatConnect)
        
        
    
    # #ip 값 넣고 chat 연결
    # def chatConnect(self):           
    #             ip=self.ip_TextEdit.toPlainText()
    #             print(ip)
    #             #self.ipconnect_btn.connect(self.client.ChatClient(ip, port))
    
    def tableWidget_doubleClicked(self):
        row = self.client_table.currentIndex().row()
        column = self.client_table.currentIndex().column()
        # self.Graph_layout.removeItem()

        
        myGUI = CustomMainWindow()
        #어떻게 widget을 없애지?
    

        self.Graph_layout.addWidget(myGUI.myFig)
        print(row, column)
    
    
    @pyqtSlot(list)
    def timeout(self, client_info):
        
        self.client_table.setRowCount(len(client_info))
        self.client_table.setColumnCount(5)
        #애초에 소팅 설정해두면 에러가 나서 끊어주고 데이터 넣고 다시 True로 바꿔줌.
        self.client_table.setSortingEnabled(False)
        for i in range(len(client_info)):
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


            self.client_table.setItem(i,1, item_refresh)

            self.client_table.setItem(i,0,QTableWidgetItem(client_info[i]))
        
        self.client_table.setSortingEnabled(True)

class MainServer :
    
    def __init__(self) :
        self.s_sock = socket(AF_INET, SOCK_STREAM)
        self.ip = ""
        self.port = 2500 #우선 포트 번호 2500으로 고정. 나중에 수정 가능
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) #다중 접속 방지
        self.s_sock.bind((self.ip, self.port)) #ip와 port를 바인드
        print("클라이언트 대기 중...")
        self.s_sock.listen(100) #접속자 100명까지
        self.accept_client()
        
    def accept_client(self) : #클라이언트가 접속할 때 실행되는 함수
        while True :
            student_client = c_socket, (ip, port) = self.s_sock.accept()
            if student_client not in clients :
                clients.append(student_client) #클라이언트 리스트에 클라이언트가 없다면 추가
                
            print(ip + " : " + str(port) + "가 연결되었습니다.")
            
            self.show_address(ip, port)
    
    def show_address(self, ip, port) : #호스트 채팅창에 ip와 port, 이름을 보여준다. 
        info_message = ("{} : {} 가 연결되었습니다.".format(ip, port))
        message_text = QTextBrowser()
        message_text.setPlainText(info_message)
        
    def send_signal(self, socket) : #표 더블 클릭을 했을 때 클라이언트에게 시그널을 보내 영상을 요청한다.
        signal_message = "1"
        socket.send(signal_message.encode('utf-8'))
    
    def show_video(self, socket) : #호스트의 캔버스에 클라이언트의 영상을 보여준다.
        pass
    
      
if __name__ =='__main__':
    app = QApplication(sys.argv)
    host_window = Host_window()
    host_window.show()
    app.exec_()
    
