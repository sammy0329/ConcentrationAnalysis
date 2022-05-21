# 딥러닝을 이용한 화상회의 집중도 분석 서비스

![image](https://user-images.githubusercontent.com/38833676/169653417-86b13159-e86e-4f45-9cda-a76792a5a0ed.png)


![image](https://user-images.githubusercontent.com/38833676/169653443-ae7c9cb3-a0c3-48f7-91cb-cc2b4c31200e.png)

딥러닝을 사용한 얼굴 감정 인식을 통해 감정 분석 결과를 집중도 가중치를 이용하여 집중도로 환산 그리고 얼굴 인식 모델을 통한 예외 상태(자리 비움, 졸음 상태)를 감지하고
이를 호스트(교수,강사,선생님)에게 제공함으로서 화상회의(수업)에서 학생 전체의 상태를 확인하고 피드백 가능하도록 하게 할 수 있다.

# 필요 라이브러리




# 사용법

모델 다운로드 링크
:https://drive.google.com/file/d/1G0YGlgfXXm4xOzsyE7yeANpkB4sIa44d/view?usp=sharing

1. 모델 다운로드 후 모델 파일을 C:drive 최상위로 이동


2.main.py를 실행


3.client or host 선택


![image](https://user-images.githubusercontent.com/38833676/169653835-35171f96-27e8-4052-946d-5faba838abc0.png)

(*호스트가 없다면 호스트 생성 필수)

4. host 생성 후 host link를 client에게 host link 제공


![image](https://user-images.githubusercontent.com/38833676/169653951-0f5798f5-c9e6-40b4-8c35-0b9a194c89a0.png)

(호스트 수업 이름 설정)

![image](https://user-images.githubusercontent.com/38833676/169653997-0bc98839-9c0e-427a-9ae5-a7eb52fa4dd8.png)

(수업 링크를 client에게 제공)

5. host link를 이용하여 client는 host에 접속

![image](https://user-images.githubusercontent.com/38833676/169654542-d807895d-f502-4b5a-92c9-91755a1e0570.png)

(link 입력)


![image](https://user-images.githubusercontent.com/38833676/169654221-39257201-8eb8-424c-9096-0577a80153fd.png)

(client 정보 입력)

6.접속 결과

![ㅇㅇㅇ](https://user-images.githubusercontent.com/38833676/169654794-ea03d74b-c139-4b1d-bd0f-7002c0ac3933.png)




