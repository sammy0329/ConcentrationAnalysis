import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib as plt
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import time
import threading
from PyQt5 import uic
import random

form_class1 = uic.loadUiType('./ui/graph.ui')[0]

class CustomMainWindow(QWidget,form_class1):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Create FRAME_A
        self.FRAME_A = QFrame(self)
        self.FRAME_A.setStyleSheet("QWidget { background-color: %s }" % QColor(210,210,235,255).name())
      
        self.myFig = CustomFigCanvas()

        # Add the callbackfunc to ..
        # myDataLoop = threading.Thread(name = 'myDataLoop', target = dataSendLoop, daemon = True, args = (self.addData_callbackFunc,))
        # myDataLoop.start()
        return 

    def addData_callbackFunc(self, value):
        self.mylist=value
        
        self.myFig.addData(value)
        return

class CustomFigCanvas(FigureCanvas, TimedAnimation):
    def __init__(self):
        self.addedData = []
        
        self.xlim = 60
        self.n = np.linspace(0, self.xlim - 1, self.xlim)
        self.y = (self.n * 0.0) + 50

        # The window
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.fig.subplots_adjust(0.1, 0.25, 0.98, 0.9) # left,bottom,right,top 
        self.ax1 = self.fig.add_subplot(111)
        
        # self.ax1 settings
        self.ax1.set_xlabel('Time', fontweight='bold')
        self.ax1.set_ylabel('Concentration Score', fontweight='bold')
        self.line1 = Line2D([], [], color='blue')
        self.line1_tail = Line2D([], [], color='red', linewidth=2)
        self.line1_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)
        self.ax1.set_xlim(0, self.xlim - 1)
        self.ax1.set_ylim(0, 1.0)

        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval = 50, blit = True)
        return

    def new_frame_seq(self):
        return iter(range(self.n.size))

    def _init_draw(self):
        lines = [self.line1, self.line1_tail, self.line1_head]
        for l in lines:
            l.set_data([], [])
        return

    def addData(self, value):
        # self.addedData.append(value)
        self.addedData=value
        print(self.addedData)
        return

    # def _step(self, *args):
    #     try:
    #         TimedAnimation._step(self, *args)
    #     except Exception as e:
    #         self.abc += 1
    #         print(str(self.abc))
    #         TimedAnimation._stop(self)
    #         pass
    #     return

    def _draw_frame(self, framedata):
        margin = 2
        while(len(self.addedData) > 0):
            self.y = np.roll(self.y, -1)
            self.y[-1] = self.addedData[0]
            del(self.addedData[0])

        self.line1.set_data(self.n[ 0 : self.n.size - margin ], self.y[ 0 : self.n.size - margin ])
        self.line1_tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]), np.append(self.y[-10:-1 - margin], self.y[-1 - margin]))
        self.line1_head.set_data(self.n[-1 - margin], self.y[-1 - margin])
        self._drawn_artists = [self.line1, self.line1_tail, self.line1_head]
        return

# class Communicate(QObject):
#     data_signal = pyqtSignal(float)

# @pyqtSlot(dict)
# def dataSendLoop(addData_callbackFunc):
#     mySrc = Communicate()
#     mySrc.data_signal.connect(addData_callbackFunc)
    
#     n = np.linspace(0, 499, 500)
#     # y = 50 + 25*(np.sin(n / 8.3)) + 10*(np.sin(n / 7.5)) - 5*(np.sin(n / 1.5))
#     y=[]
#     for i in range(100):
#         y.append(random.randint(0,100))
#     i = 0

#     while(True):
#         if(i > 60):
#             break
#         time.sleep(0.1)
#         # time.sleep(0.5)
#         mySrc.data_signal.emit(y[i]) # <- Here you emit a signal!
#         i += 1

if __name__== '__main__':
    app = QApplication(sys.argv)
    # QApplication.setStyle(QStyleFactory.create('Plastique'))
    myGUI = CustomMainWindow()
    sys.exit(app.exec_())