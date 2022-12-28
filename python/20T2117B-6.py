from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5 import QtCore 
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import numpy as np
import pyqtgraph as pg
import sys

##################process############################
class createNumber:
    def __init__(self):
        self.number = 0
        self.time = 0
        self.number_list = []
        self.time_list = []

    def createList(self):
        self.number = np.random.random()#0～1の小数点をランダムに生成
        self.time += 0.01
        return self.number, self.time

########################pyqtgraph###########################################
class pygraph(createNumber):
    def __init__(self):
        super().__init__()
        self.maxX = 100
        self.app = QtGui.QApplication(sys.argv)
        self.gui = QWidget()
        self.win = pg.GraphicsWindow(size=(300,300),border=True,parent=self.gui)
        self.graph = self.win.addPlot(title="pyqtgraph")

    def setPg(self):
        self.gui.setGeometry(400,300,500,500)
        self.win.move(10,50)

    def axis(self):
        self.setPg()
        self.graph.setLabel('left',"Gravity", units='g')
        self.graph.setLabel('bottom',"Time", units='s')  
        self.xaxis = self.graph.getAxis('bottom')
        self.yaxis = self.graph.getAxis('left')
        self.graph.showGrid(x=True, y=True)

    def plot(self):
        self.axis()
        self.getValue()
        self.curve = self.graph.plot(self.time_list, self.number_list, pen=pg.mkPen(width=2, color='b'))
        self.timerJob()

    def timerJob(self):
        self.timer = QTimer(self.gui)
        self.timer.timeout.connect(self.setLine)
        self.timer.start(10)#0.01 seconds

    def getValue(self):
        global time
        self.number, self.time = super().createList()
        self.number_list.append(self.number)
        self.time_list.append(self.time)
        self.graph.setRange(xRange=[0,self.time_list[len(self.time_list)-1]],yRange=[0,1.0])

    def setLine(self):
        self.getValue()
        self.curve.setData(self.time_list, self.number_list)
    
    def active(self):
        self.gui.show()
        sys.exit(self.app.exec_())

##################matplotlib###########################
class matplot(createNumber):
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

    def setData(self):
        self.setArea()
        self.line, = self.graph.plotarea.plot(self.time_list, self.number_list, color='blue', lw=1)
        self.graph.plotarea.axes.tick_params(axis='x',labelrotation=90)
        self.timerJob()

    def setLine(self):
        self.line.set_data(self.time_list, self.number_list)
        self.graph.plotarea.set_xticks(self.time_list)
        self.graph.plotarea.axis([self.time_list[0],self.time_list[len(self.time_list)-1],0,1.0])
        self.graph.draw()

    def getValue(self):
        self.number, self.time = super().createList()
        self.number_list.append(self.number)
        self.time_list.append(self.time)
        self.setLine()

    def timerJob(self):
        self.timer = QTimer(self.gui)#set time
        self.timer.timeout.connect(self.getValue)#active display value
        self.timer.start(10)#0.01 seconds

    def active(self):
        self.gui.show()
        sys.exit(self.app.exec_()) 


pg.setConfigOptions(antialias=True)
pg.setConfigOptions(foreground='k')
pg.setConfigOptions(background='w')
pygraph = pygraph()
pygraph.plot()
pygraph.active()  

'''
matplot = matplot()
matplot.setData()
matplot.active()
'''