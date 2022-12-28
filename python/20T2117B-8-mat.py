import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import numpy as np
import datetime
import matplotlib.dates as mdates

class matplotlib:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.gui = QMainWindow()
        #create subWindow　(400, 300)
        self.mpfig = Figure(figsize=(4,3), dpi=100, facecolor="magenta",edgecolor="black",linewidth=10)
        #subWindowにgrathを書き込む
        self.graph = FigureCanvas(self.mpfig)
        #NavigationToolを有効にする
        self.toolbar = NavigationToolbar(self.graph,self.gui)
        self.basetime = datetime.datetime.now().replace(microsecond=0)
        
    def kadai1(self):
        self.gui.setWindowTitle('PyQt5 Window')
        self.gui.setGeometry(400,200,500,500)
        #Toolの追加
        self.gui.addToolBar(QtCore.Qt.BottomToolBarArea,self.toolbar)
        #subplotの追加　(1行目,1列目,1番目)
        self.graph.plotarea = self.mpfig.add_subplot(1,1,1)
        self.graph.move(10,50)
        #windowであるguiの中にグラフを追加
        #self.mpfig.tight_layout()
        self.graph.setParent(self.gui)

    def kadai2(self):
        self.kadai1()
        self.graph.plotarea.set_title('Trigonometric Functions',fontsize=15,color='green',loc='center')
        self.graph.plotarea.set_xlabel('Time\n(s)',labelpad=5,position=(0.5,0),horizontalalignment='center')
        #verticalalignmentは縦軸に対する揃え方である。
        self.graph.plotarea.set_ylabel('Voltage(V)',labelpad=5,position=(0,1),horizontalalignment='right',verticalalignment='bottom',rotation=90)

    def kadai3(self):
        self.kadai2()
        #plotarea.axis([x_min, x_max, y_min, y_max])
        self.graph.plotarea.axis([0,3,-2,2])
        #x_scale of place
        self.graph.plotarea.set_xticks([0, 0.5, 1, 1.5, 2.0, 2.5, 3.0])
        #y_scale of place
        self.graph.plotarea.set_yticks([-2, -1, 0, 1, 2])
        self.graph.plotarea.grid(axis='x')#grid線追加
        self.graph.plotarea.grid(axis='y')
        #number→letter
        self.graph.plotarea.set_xticklabels(['0','0.5','1.0', '1.5', '2.0', '2.5', '3.0'],rotation=90)
        self.graph.plotarea.set_yticklabels(['A','B','C', 'D', 'E'])

    def kadai4(self):
        self.kadai3()
        #text追加
        self.graph.plotarea.text(1, -2, 'Function: $y(t)=t^3-2t^2+1$',horizontalalignment='center')
        #self.graph.plotarea.text(0.5,1,'Function: $y(t)=t_1^2$')

    def active(self):
        self.gui.show()
        sys.exit(self.app.exec_()) 

matplot = matplotlib()
matplot.kadai4()
matplot.active() 