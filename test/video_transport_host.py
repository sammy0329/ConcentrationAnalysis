import cv2
import socket
import pickle
import struct

class transporter():
    def __init__(self):
        super().__init__()
        self.ip = '192.168.0.5'
        self.port = 50001

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(10)

        self.data_buffer = b""
        self.data_size = struct.calcsize("L")

    def get_video(self):
        print("호출완료1")
        client_socket, address = self.server_socket.accept()
        print("호출완료2")
        while True:
            print("호출완료3")
            # 설정한 데이터의 크기보다 버퍼에 저장된 데이터의 크기가 작은 경우
            while len(self.data_buffer) < self.data_size:
                # 데이터 수신
                self.data_buffer += client_socket.recv(4096)

            # 버퍼의 저장된 데이터 분할
            packed_data_size = self.data_buffer[:self.data_size]
            self.data_buffer = self.data_buffer[self.data_size:]

            frame_size = struct.unpack(">L", packed_data_size)[0]

            # 프레임 데이터의 크기보다 버퍼에 저장된 데이터의 크기가 작은 경우
            while len(self.data_buffer) < frame_size:
                # 데이터 수신
                self.data_buffer += client_socket.recv(4096)

            # 프레임 데이터 분할
            frame_data = self.data_buffer[:frame_size]
            self.data_buffer = self.data_buffer[frame_size:]

            print("수신 프레임 크기 : {} bytes".format(frame_size))

            # loads : 직렬화된 데이터를 역직렬화
            frame = pickle.loads(frame_data)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

            # 프레임 출력
            cv2.imshow('Frame', frame)

            # 'q' 키를 입력하면 종료
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        client_socket.close()
        self.server_socket.close()
        cv2.destroyAllWindows()