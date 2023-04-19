# 딥러닝을 이용한 화상회의 집중도 분석 서비스
### 한화시스템 레이다 연구소-광운대학교 산학연계 프로젝트
## 프로젝트 선정 배경
<p> 화상 수업시 선생님은 여러명의 학생들이 집중하는지의 여부를 한번에 확인하기 어렵다.</p>
<p>☞ 집중하지 않는 혹은 자리를 비우거나 졸고 있는 등.. 특이사항이 있는 학생들을 분석해서 알려준다면 학생들을 관리하는데 도움이 되지 않을까?? 🤷🏻‍♂️</p>

## 서비스 소개
<img width="528" alt="서비스소개" src="https://user-images.githubusercontent.com/38906420/233032408-f6f637c5-0697-42ad-aeb5-d08cf250ec73.png"><br />
<img width="528" alt="호스트정리" src="https://user-images.githubusercontent.com/38906420/233037411-783468d0-9814-41c0-8dd6-f86f9f62e9e4.png"><br />
<p>💡 화상수업시 선생님에게 <b>딥러닝을 사용한 감정 분석 결과를 *관련 논문을 참고한 집중도 가중치를 이용하여 집중도로 환산</b>(상,중,하) 및 졸음, 하품, 자리비움에 대한 보조지표 제공.</p>
<p>*관련 논문</p>
<img width="591" alt="집중도 논문" src="https://user-images.githubusercontent.com/38906420/233044991-2ae400b6-bdab-4d9d-a457-ae5cabff2799.png">

## 서비스 활용 방안
<p>✔️ 학생별 집중도를 제공해 빠른 피드백이 가능하도록 도움.</p>
<p>✔️ 데이터베이스에 학생 집중지표를 시간에 따라 저장해 통계 서비스와 같은 강의 사후 평가에 활용 가능.</p>

## 기술 스택
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/pytorch-E34F26?style=for-the-badge&logo=PyTorch&logoColor=white"> <img src="https://img.shields.io/badge/Firebase-F7DF1E?style=for-the-badge&logo=Firebase&logoColor=black">

## 협업 툴
<img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white"> <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white"> <img src="https://img.shields.io/badge/slack-339AF0?style=for-the-badge&logo=slack&logoColor=white">
## 서비스 아키텍처
<img width="783" alt="아키텍처" src="https://user-images.githubusercontent.com/38906420/233021226-323e9ec2-6138-4081-bb79-599d401c25bc.png">


## 필요 라이브러리 & 모델 다운로드
[lib.txt](https://github.com/sammy0329/ConcentrationAnalysis/files/8747761/lib.txt)<br />
https://drive.google.com/file/d/1G0YGlgfXXm4xOzsyE7yeANpkB4sIa44d/view?usp=sharing

## 사용법


<p>1. 모델 다운로드 후 모델 파일을 C:drive 최상위로 이동</p>


<p>2. main.py를 실행</p>


<p>3. client or host 선택</p>


![image](https://user-images.githubusercontent.com/38833676/169653835-35171f96-27e8-4052-946d-5faba838abc0.png)

<p>4-1. host로 입장시 식별할 수 있는 수업명 입력해 방을 만들고, 암호화된 수업 링크를 client에게 전달한 뒤 들어올 때까지 대기하기..👨‍🏫</p>
<p>💡 host가 방을 만들면 firebase에 입력한 수업명을 제목으로 폴더가 만들어지고, 해당 방에 들어온 client의 집중도 관련 데이터들이 적재</p>

![image](https://user-images.githubusercontent.com/38833676/169653951-0f5798f5-c9e6-40b4-8c35-0b9a194c89a0.png)


![image](https://user-images.githubusercontent.com/38833676/169653997-0bc98839-9c0e-427a-9ae5-a7eb52fa4dd8.png)



<p>4-2. client는 host에게 전달받은 link 입력 후, 학번과 이름을 입력하고 방에 입장 🖥️</p>

![image](https://user-images.githubusercontent.com/38833676/169654542-d807895d-f502-4b5a-92c9-91755a1e0570.png)


![image](https://user-images.githubusercontent.com/38833676/169654221-39257201-8eb8-424c-9096-0577a80153fd.png)


<p>⭐️ host에서 본 client들 집중도 분석 화면</p>

![image](https://user-images.githubusercontent.com/38833676/169654794-ea03d74b-c139-4b1d-bd0f-7002c0ac3933.png)




