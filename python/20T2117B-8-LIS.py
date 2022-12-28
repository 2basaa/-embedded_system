import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import numpy as np
import datetime
import matplotlib.dates as mdates
import math
import spidev
import pyqtgraph as pg
import sys

lis = spidev.SpiDev()#start spi
lis.open(0,0)#SPIO CE0
lis.max_speed_hz = 10000#maxspeed 10000Hz
lis.bits_per_word=8#1word = 8bit

##################process############################
class process:
    def __init__(self):
        self.read_reg1 = 0xa0#read reg1
        self.write_reg1 = 0x20#write reg1
        self.read_reg4 = 0xa3#read reg4
        self.write_reg4 = 0x23#write reg4
        self.x_address = 0xa8#read xaddress
        self.y_address = 0xaa#read yaddress
        self.z_address = 0xac#read zaddress
        self.x = 0#x_value
        self.y = 0#y_value
        self.z = 0#z_value
        self.time = datetime.datetime.now().replace(microsecond=0)
        self.time_list = []
        self.x_list = []
        self.y_list = []
        self.z_list = []
        
    def setLis3dh(self):#set lis3dh
        #↓appdate_data 1 second
        lis.xfer2([self.write_reg1,0x17])#1hz
        lis.xfer2([self.write_reg4,0x00])#scale is 2g

    def readlis3dh(self, reg2):#get lis3dhdata
        self.rcv = lis.xfer2([reg2,0x00])#get high_data
        self.g = self.rcv[1]
        self.rcv = lis.xfer2([reg2+1,0x00])#get_low_data
        self.g = (self.g | self.rcv[1]<<8)>>4#12bit
        return self.g#get sensor_data

    def judgeSign(self, address):#cahnge sign
        self.judge = self.readlis3dh(address)#get sensor data
        if self.judge >= 2048:#minus
            self.judge -= 4096
        else:#plus
            self.judge = self.judge  
        return self.judge#get signed data
   
    def accelerationValue(self, address):#set acceleration
        self.gravity = self.judgeSign(address)#signed data
        self.acceleration_value = self.gravity / 1024
        self.value =  round(self.acceleration_value, 2)#2 decimal places
        return self.value
    
    def active(self):
        self.x = self.accelerationValue(self.x_address)#get x_acceleration
        self.y = self.accelerationValue(self.y_address)#get y_acceleration
        self.z = self.accelerationValue(self.z_address)#get z_acceleration
        self.time += datetime.timedelta(seconds=0.5)
        return self.x, self.y, self.z, self.time

##################matplotlib###########################
class matplot(process):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.gui = QMainWindow()
        #create subWindow　(400, 300)
        self.mpfig = Figure(figsize=(4,3), dpi=100, facecolor="magenta",edgecolor="black",linewidth=10)
        #subWindowにgrathを書き込む
        self.graph = FigureCanvas(self.mpfig)
        #NavigationToolを有効にする
        self.toolbar = NavigationToolbar(self.graph,self.gui)
        
    def window(self):
        self.gui.setGeometry(400,300,500,500)
        #Toolの追加
        self.gui.addToolBar(QtCore.Qt.BottomToolBarArea,self.toolbar)
        #subplotの追加　(1行目,1列目,1番目)
        self.graph.plotarea = self.mpfig.add_subplot(1,1,1)
        self.graph.move(10,50)
        #windowであるguiの中にグラフを追加
        self.mpfig.tight_layout()
        self.graph.setParent(self.gui)

    def setGraph(self):
        self.window()
        self.graph.plotarea.set_title('matplotlib',fontsize=15,color='black',loc='center')
        self.graph.plotarea.set_xlabel('Time(s)',labelpad=5,position=(0.5,0),horizontalalignment='center')
        #verticalalignmentは縦軸に対する揃え方である。
        self.graph.plotarea.set_ylabel('Gravity(g)',labelpad=5,position=(0,1),horizontalalignment='right',verticalalignment='bottom',rotation=90)

    def setArea(self):
        self.setGraph()
        self.graph.plotarea.grid(axis='x')#grid線追加
        self.graph.plotarea.grid(axis='y')
        self.formatter = mdates.DateFormatter('%M:%S')
        self.graph.plotarea.xaxis.set_major_formatter(self.formatter)

    def setData(self):
        self.setArea()
        self.line1, = self.graph.plotarea.plot(self.time_list, self.x_list, color='red', lw=1)
        self.line2, = self.graph.plotarea.plot(self.time_list, self.y_list, color='blue', lw=1)
        self.line3, = self.graph.plotarea.plot(self.time_list, self.z_list, color='green', lw=1)
        self.graph.plotarea.axes.tick_params(axis='x',labelrotation=90)
        self.timerJob()

    def setLine(self):
        self.line1.set_data(self.time_list, self.x_list)
        self.line2.set_data(self.time_list, self.y_list)
        self.line3.set_data(self.time_list, self.z_list)
        self.graph.plotarea.set_xticks(self.time_list)
        self.graph.plotarea.axis([self.time_list[0],self.time_list[len(self.time_list)-1],-1.5,1.5])
        self.graph.draw()

    def getValue(self):
        self.x, self.y, self.z, self.time = super().active()
        self.x_list.append(self.x)
        self.y_list.append(self.y)
        self.z_list.append(self.z)
        self.time_list.append(self.time)
        self.setLine()

    def timerJob(self):
        self.timer = QTimer(self.gui)#set time
        self.timer.timeout.connect(self.getValue)#active display value
        self.timer.start(500)#0.5 seconds

    def active(self):
        self.gui.show()
        sys.exit(self.app.exec_()) 

process = process()
process.setLis3dh()
matplot = matplot()
matplot.setData()
matplot.active()