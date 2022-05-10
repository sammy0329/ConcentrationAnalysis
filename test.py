from socket import *
from threading import *
import base64
import numpy

from scipy import rand
from graph import *
import random
import cv2

clients=[]

class MainServer(QThread) :
    
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
    mywindow = MainServer()
    mywindow.show()
    app.exec_()