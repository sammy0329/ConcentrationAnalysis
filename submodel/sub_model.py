import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import schedule
from PyQt5.QtCore import QThread

class sub_model(QThread):
    def __init__(self, cv_cap):
        super().__init__()
        self.cap = cv_cap
    
        self.detector = FaceMeshDetector(maxFaces=1)
        self.plotY = LivePlot(640, 360, [20, 50], invert=True)

        self.ratioList = []
        self.mouth_ratioList=[]
        self.nose_ratioList=[]
        self.blinkCounter = 0
        self.counter = 0
        self.color = (255, 0, 255)
 
    def initialization(self):
    
        self.counter= 0
        self.blinkCounter=0
        self.ratioList = []


    def warning(self) :   # 잘 때
        print("sleep")            

    def leaving(self) : # 얼굴 감지 안될 때

        print("leaving")

    def yawning(self) : # 하품할 때

        print("yawning")

    def run(self):
        while True:

            schedule.run_pending()
    
            if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
 
            success, img = self.cap.read()
            img, faces = self.detector.findFaceMesh(img, draw=False)
    
 
            if faces:
                face = faces[0]

 
        #입크기에 따른 하품 판단
                self.mouthLeft= face[48]
                self.mouthRight= face[54]
                self.mouthUp= face[51]
                self.mouthDown= face[57]
                self.mouth_lenghtVer, _ = self.detector.findDistance(self.mouthUp, self.mouthDown)
                self.mouth_lenghtHor, _ = self.detector.findDistance(self.mouthLeft, self.mouthRight)
        
                mouth_ratio = int((self.mouth_lenghtVer / self.mouth_lenghtHor) * 100)
                self.mouth_ratioList.append(mouth_ratio)
                if len(self.mouth_ratioList) > 3:
                    self.mouth_ratioList.pop(0)
                mouth_ratioAvg = sum(self.mouth_ratioList) / len(self.mouth_ratioList)
        
        
                noseUp=face[27]
                noseDown=face[30]
                chin=face[8]
        

        
        
        #감고있는 거 # 자는거 체크
                leftUp = face[159]
                leftDown = face[23]
                leftLeft = face[130]
                leftRight = face[243]
                lenghtVer, _ = self.detector.findDistance(leftUp, leftDown)
                lenghtHor, _ = self.detector.findDistance(leftLeft, leftRight)

 
                ratio = int((lenghtVer / lenghtHor) * 100)
                self.ratioList.append(ratio)
                if len(self.ratioList) > 3:
                    self.ratioList.pop(0)
                ratioAvg = sum(self.ratioList) / len(self.ratioList)
 
          
                if ratioAvg > 32 :
                    self.initialization()
                else :
                    self.blinkCounter += 1
                    print(self.blinkCounter)
                if(self.blinkCounter>1000):
                    self.warning()
                                 

                if mouth_ratioAvg>80:
                   self.yawning()
            

            else:
                self.leaving()

    
if __name__ == "__main__":

    cv_cap = cv2.VideoCapture(0)
    sub = sub_model(cv_cap)
    sub.run()