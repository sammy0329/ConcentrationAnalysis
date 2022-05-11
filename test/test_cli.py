import socket
from threading import Thread

HOST = '192.168.0.7'    # 내가 접속할 서버의 ip주소
PORT = 9009                 # 서버의 포트 번호 (서로 같아야 연결 가능)


def rcvMsg(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(data.decode())
        except:
            pass


def runChat():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        t = Thread(target=rcvMsg, args=(sock,))
        t.daemon = True
        t.start()

        while True:
            msg = input()
            if msg == '/quit':
                sock.send(msg.encode())
                break

            sock.send(msg.encode())


runChat()