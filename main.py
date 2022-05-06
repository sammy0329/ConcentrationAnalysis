from host import *
from client import *
from cryptography.fernet import Fernet
import json

key_path = "resource/db_auth_key.json"

mainform_class = uic.loadUiType('./ui/main.ui')[0]

with open (key_path, "r") as f:
    data = json.load(f)
    
key=data['class_key'].encode('utf-8')
cipher_suite = Fernet(key)
        
class MyWindow(QMainWindow, mainform_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.host_btn.clicked.connect(self.button_host)
        self.client_btn.clicked.connect(self.button_client)
    
    def button_host(self):
        self.hide()
        
        #classname과 server ip 주소를 암호화
        self.classname, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your Class Nmae:')
       
        if ok:
            self.host_window=Host_window()
            
            self.class_serverip=classname+'@'+ self.host_window.local_ip
            
            self.encrypt_text=cipher_suite.encrypt(self.class_serverip.encode())
            # plain_text = cipher_suite.decrypt(encrypt_text)
            self.host_window.code_text.setText(self.encrypt_text.decode('utf-8'))
            print(self.encrypt_text.decode('utf-8'))
            # print(plain_text)
        else:
            self.show()

        
    def button_client(self):
        self.hide()
        
        self.encrypt_text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your Server IP:')

        
        if ok:
            self.decrypt_text = cipher_suite.decrypt(self.encrypt_text.encode('utf-8'))
            self.str_data = self.decrypt_text.decode('utf-8')
            self.dir_name,self.server_ip=self.str_data.split('@')
            print(self.dir_name,self.server_ip)
            
            self.client_info_window=Client_info_window()
        else:
            self.show()

if __name__ =='__main__':
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()