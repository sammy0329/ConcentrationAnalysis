from graph import *
import db_auth as dbs
import time
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import socket
import random
# from scipy import rand
from socket import *
from threading import *
import base64
import numpy
import cv2


form_class = uic.loadUiType('./ui/Widget_test.ui')[0]

client_info=[]
exlist=[]
hostname = gethostname()
local_ip = gethostbyname(hostname)
clients = [] #클라이언트 리스트
sockets = [] #소켓 리스트

class Clientclass(QThread):
    timeout = pyqtSignal(list)    # 사용자 정의 시그널
    
    def __init__(self):
        super().__init__()
        self.client_info=[]           # 초깃값 설정
        
    def run(self):      
        while True:
            self.db_dict = dbs.dir.get()
            self.client_info=[]
            for i, each in enumerate(self.db_dict):
                self.client_info.append(each)
            self.timeout.emit(self.client_info)
            
            time.sleep(3)
      
# class Host_window(QMainWindow, form_class):  
class Host_window(QWidget, form_class):
    def __init__(self):
        super().__init__()
        self.local_ip=socket.gethostbyname(hostname)
        self.setupUi(self)
        self.cli=Clientclass()
        self.cli.start()
        self.cli.timeout.connect(self.timeout)   # 시그널 슬롯 등록
        self.setupUI()
        
        self.show()
        
    def setupUI(self):
        self.client_table.doubleClicked.connect(self.tableWidget_doubleClicked)
        self.client_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    
    def tableWidget_doubleClicked(self):
        row = self.client_table.currentIndex().row()
    
        #더블클릭시 클라이언트 이름 따오기
        client_name = self.client_table.item(row, 0).text()
        print(client_name)
        
        myGUI = CustomMainWindow()

        for i in reversed(range(self.Graph_layout.count())):
            self.Graph_layout.removeItem(self.Graph_layout.itemAt(i))

        self.Graph_layout.addWidget(myGUI.myFig)
        

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

class MainServer(QThread) :
    
    def __init__(self) :
        self.hostClass = Host_window()
        self.hostClass.start()
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
        self.show_thread(socket)

    def show_thread(self, socket) : #시그널을 보낸 후 show_thread 실행
        show_th = Thread(target = self.show_video, args = (socket, ))
        show_th.start()
    
    def show_video(self, socket) : #호스트의 캔버스에 클라이언트의 영상을 보여준다.
        while True :
            try :
                length = self.recvall(socket, 64)
                receive_length = length.decode('utf-8')
                stringData = self.recvall(socket, int(receive_length))
                data = numpy.frombuffer(base64.b64decode(stringData), numpy.uint8)
                show_image = cv2.imdecode(data, 1)
                self.Input_cam(show_image)
            except :
                socket.close()

    def recvall(sock, count) : #수신받은 후 buf 반환
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf

if __name__ =='__main__':
    app = QApplication(sys.argv)
    host_window = Host_window()
    host_window.show()
    app.exec_()
