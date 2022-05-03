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
import socket
from test_graph import *


# form_class = uic.loadUiType('./ui/test1.ui')[0]
# form_class = uic.loadUiType('./ui/test_graph.ui')[0]
form_class = uic.loadUiType('./ui/Widget_test.ui')[0]

key_path = "test-db-b261c-firebase-adminsdk-ddkpv-ff4ed08001.json"
db_url = "https://test-db-b261c-default-rtdb.firebaseio.com/"
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {'databaseURL' : db_url})
dir = db.reference()
client_info=[]

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)


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
        for i in range(len(client_info)):
            self.client_table.setItem(i,0,QTableWidgetItem(client_info[i]))
      
    
if __name__ =='__main__':
    app = QApplication(sys.argv)
    host_window = Host_window()
    host_window.show()
    app.exec_()
    