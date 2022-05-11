import cv2
import socket
import pickle
import struct

class transporter():
    def __init__(self):
        super().__init__()
        self.ip = '192.168.0.5'
        self.port = 50001
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def send_video(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # 서버와 연결
            client_socket.connect((self.ip, self.port))
            print("연결 성공")

            # 메시지 수신
            while True:
                retval, frame = self.capture.read()
                retval, frame = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])

                frame = pickle.dumps(frame)

                print("전송 프레임 크기 : {} bytes".format(len(frame)))
                client_socket.sendall(struct.pack(">L", len(frame)) + frame)

        capture.release()