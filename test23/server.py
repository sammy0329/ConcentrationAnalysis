# threading 모듈을 이용한 TCP 멀티 채팅 서버 프로그램

from socket import *
from threading import *

class MultiChatServer :
    #__init__()에서 선언할 수 없는 변수는
    #모든 메소드에서 사용할 수 있도록 클래스 변수로 선언

    clients = []
    final_received_message = "" #최종 수신된 메시지

    def __init__(self) :
        self.s_sock = socket(AF_INET, SOCK_STREAM)
        self.ip = ""
        self.port = 2500
        self.s_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.s_sock.bind((self.ip, self.port))
        print("클라이언트 대기 중....")
        self.s_sock.listen(100)
        self.accept_client()
    
    #연결 클라이언트 소켓을 목록에 추가하고 스레드를 생성하여 데이터를 수신한다
    def accept_client(self) :
        while True :
            client = c_socket, (ip, port) = self.s_sock.accept()
            if client not in self.clients :
                self.clients.append(client) # 접속된 소켓을 목록에 추가
            print(ip, " : ", str(port), "가 연결되었습니다.")
            cth = Thread(target = self.receive_messages, args = (c_socket, ))
            #수신 스레드
            cth.start() #스레드 시작

    #데이터를 수신하여 모든 클라이언트에게 전송한다
    def receive_messages(self, c_socket) :
        while True :
            try :
                incoming_message = c_socket.recv(256)
                if not incoming_message : #연결이 종료됨
                    break
            except :
                continue
            
            else :
                self.final_received_message = incoming_message.decode("UTF-8")
                print(self.final_received_message)
                self.send_all_clients(c_socket)
        
        c_socket.close()

    def send_all_clients(self, senders_socket) :
        for client in self.clients : #목록에 있는 모든 소켓에 대해
            socket, (ip, port) = client
            if socket is not senders_socket : #송신 클라이언트는 제외
                try :
                    socket.sendall(self.final_received_message.encode())
                
                except : #연결 종료
                    self.clients.remove(client) #소켓 제거
                    print("{}, {} 연결이 종료되었습니다.".format(ip, port))

if __name__ == "__main__" :
    MultiChatServer()

