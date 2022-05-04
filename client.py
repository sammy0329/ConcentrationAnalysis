import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
client_form_class = uic.loadUiType("./ui/client.ui")[0]
client_info_form_class = uic.loadUiType("./ui/client_info.ui")[0]

class Client_window(QWidget, client_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
        
class Client_info_window(QWidget, client_info_form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.commit_btn.clicked.connect(self.button_commit)
        self.show()
        
    def button_commit(self):
        self.hide()
        self.client_window=Client_window()
         
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Client_info_window()
    myWindow.show()
    app.exec_()