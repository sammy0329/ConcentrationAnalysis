import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import schedule
from PyQt5.QtCore import QThread
import db_auth as dbs

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
        self.yawn_num = 0

    def initialization(self):
        self.blinkCounter=0
        self.ratioList = []

    def warning(self) :   # 잘 때
        query = "{{'{}':'{}'}}".format("status", "sleep")
        query = eval(query)
        dbs.dir.update(query)
        print("sleep")

    def leaving(self) : # 얼굴 감지 안될 때
        query = "{{'{}':'{}'}}".format("status", "leave")
        query = eval(query)
        dbs.dir.update(query)
        print("leave")

    def normal(self):
        query = "{{'{}':'{}'}}".format("status", "")
        query = eval(query)
        dbs.dir.update(query)
        print("leave")

    def run(self):
        while True:
            schedule.run_pending()
    
            if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
 
            success, img = self.cap.read()
            img, faces = self.detector.findFaceMesh(img, draw=False)
 
            if faces:
                face = faces[0]
                self.normal()

        #감고있는 거 자는거 체크
                leftUp = face[159]
                leftDown = face[23]
                leftLeft = face[130]
                leftRight = face[243]
                lenghtVer, _ = self.detector.findDistance(leftUp, leftDown)
                lenghtHor, _ = self.detector.findDistance(leftLeft, leftRight)

 
                ratio=int((lenghtVer/lenghtHor)*100)
                self.ratioList.append(ratio)
                if len(self.ratioList) > 3:
                    self.ratioList.pop(0)
                ratioAvg=sum(self.ratioList) / len(self.ratioList)

                if ratioAvg>32 :
                    self.initialization()
                    self.normal()
                else :
                    self.blinkCounter += 1
                if self.blinkCounter > 1000 :
                    self.warning()

            else:
                self.leaving()

    
if __name__ == "__main__":
    cv_cap = cv2.VideoCapture(0)
    sub = sub_model(cv_cap)
    sub.run()