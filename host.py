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

form_class = uic.loadUiType('./ui/Widget_test.ui')[0]

client_info=[]
exlist=[]
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

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
            
if __name__ =='__main__':
    app = QApplication(sys.argv)
    host_window = Host_window()
    host_window.show()
    app.exec_()