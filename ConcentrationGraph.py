import sys, os, random
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
import random
from PyQt5.QtChart import QLineSeries, QChart, QValueAxis, QDateTimeAxis
from PyQt5.QtCore import Qt, QDateTime
import matplotlib.pyplot as plt
from PyQt5 import uic

import matplotlib.dates as md
import time
import datetime as dt

form_class = uic.loadUiType('./ui/Widget_test.ui')[0]

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111, xlim=(0, 50), ylim=(0, 100))
        self.compute_initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        fig.subplots_adjust(0.1, 0.1, 0.95, 0.9) # left,bottom,right,top 
        # fig.tight_layout()

    def compute_initial_figure(self):
        pass


class AnimationWidget(QWidget,form_class):
    def __init__(self):
        # QMainWindow.__init__(self)
        super().__init__()
        self.setupUi(self)
        self.canvas = MyMplCanvas(self, width=10, height=8, dpi=100)
       

        self.Graph_layout.addWidget(self.canvas)

        self.x = np.arange(50)
        print(self.x)

        self.y = np.ones(50, dtype=np.float)*np.nan
        
        self.line, = self.canvas.axes.plot(self.x, self.y, animated=True, lw=2)

        self.on_start()

    def update_line(self, i):
        y = random.randint(0,100)
        old_y = self.line.get_ydata()
        new_y = np.r_[old_y[1:], y]
        self.line.set_ydata(new_y)
  
        # print(self.y)
        return [self.line]
        
        

    def on_start(self):
        self.ani = animation.FuncAnimation(self.canvas.figure, self.update_line,blit=True, interval=1000)
      

if __name__ == "__main__":
    qApp = QApplication(sys.argv)
    aw = AnimationWidget()
    aw.show()
    sys.exit(qApp.exec_())