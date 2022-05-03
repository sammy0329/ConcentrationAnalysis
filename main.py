import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
# import PyQt5.QtWidgets as qtwid
from PyQt5.QtCore import *
from host import *
from client import *


mainform_class = uic.loadUiType('./ui/main.ui')[0]

class MyWindow(QMainWindow, mainform_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.host_btn.clicked.connect(self.button_host)
        self.client_btn.clicked.connect(self.button_client)
    
    def button_host(self):
        self.hide()
        self.host_window=Host_window()
        # self.host_window.exec()
        # self.show()

    def button_client(self):
        self.hide()
        self.client_info_window=Client_info_window()
        
if __name__ =='__main__':
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()

