import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot
import schedule
from PyQt5.QtCore import QThread
import db_auth as dbs
from firebase_admin import db

class sub_model(QThread):
    def __init__(self, cv_cap, base_dir):
        super().__init__()
        self.cap = cv_cap
        self.base_dir = base_dir + "/학생상태"

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

    def status_change(self, status):
        query = "{{'{}':'{}'}}".format("status", status)
        query = eval(query)
        dbs.dir = db.reference(self.base_dir)
        dbs.dir.update(query)

    def run(self):
        while True:
            schedule.run_pending()
    
            if self.cap.get(cv2.CAP_PROP_POS_FRAMES) == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
 
            success, img = self.cap.read()
            img, faces = self.detector.findFaceMesh(img, draw=False)
 
            if faces:
                face = faces[0]
                self.status_change("normal")

        # 감고있는 거 자는거 체크
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
                    self.status_change("normal")
                    print("check1")
                else :
                    self.blinkCounter += 1

                if self.blinkCounter > 1000 :
                    self.status_change("sleeping")
                    print("check2")

            else:
                self.status_change("leaving")
                print("check3")