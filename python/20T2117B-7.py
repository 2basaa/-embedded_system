import spidev
import math
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

lis = spidev.SpiDev()#start spi
lis.open(0,0)#SPIO CE0
lis.max_speed_hz = 10000#maxspeed 10000Hz
lis.bits_per_word=8#1word = 8bit

###################main_process#######################
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
        self.get_axis = 0#axis_data
        
    def setLis3dh(self):#set lis3dh
        #↓appdate_data 1 second
        lis.xfer2([self.write_reg1,0x17])#1hz
        lis.xfer2([self.write_reg4,0x00])#scale is 2g
    
    def createList(self, data):#create 8bit of list
        self.data_list = []#create list
        self.quotient = 0
        self.i = 7
        for self.num in range(8):
            self.quotient = data // pow(2, self.i)#create data_list[0]~data_list[7]
            if data >= pow(2, self.i):#data >= 2^i
                data -= pow(2, self.i)#data - 2^i
            self.data_list.append(self.quotient)#append quotient
            self.i -= 1
        return self.data_list #get data_list
    
    def getScale(self):#get information of ctrl_reg4 
        self.reg4 = lis.xfer2([self.read_reg4,0x00])
        return self.reg4[1]#get information of ctrl_reg4
    
    def changeScale(self, index_number):
        if index_number == 0:
            lis.xfer2([self.write_reg4,0x00])#scale is 2g
        elif index_number == 1:
            lis.xfer2([self.write_reg4,0x10])#scale is 4g
        elif index_number == 2:
            lis.xfer2([self.write_reg4,0x20])#scale is 8g
        elif index_number == 3:
            lis.xfer2([self.write_reg4,0x30])#scale is 16g
        
    def getAxis(self):#get information of ctrl_reg1
        self.reg1 = lis.xfer2([self.read_reg1,0x00])
        return self.reg1[1]#get information of ctrl_reg1
    
    def changeXen(self, reg1, data):#change Xen
        if reg1[7] == 0:#Xen is abled→disabled
            data += 1
        elif reg1[7] == 1:#Xen is disabled→abled
            data -= 1
        lis.xfer2([self.write_reg1,data])#changeXendata
        
    def changeYen(self, reg1, data):#change Yen
        if reg1[6] == 0:#Yen is abled→disabled
            data += 2
        elif reg1[6] == 1:#Yen is disabled→abled
            data -= 2
        #print(hex(data))
        lis.xfer2([self.write_reg1,data])#changeYendata   
    
    def changeZen(self, reg1, data):#changeZen
        if reg1[5] == 0:#Zen is abled→disabled
            data += 4
        elif reg1[5] == 1:#Zen is disabled→abled
            data -= 4
        #print(hex(data))
        lis.xfer2([self.write_reg1,data])#changeZendata
        
    def changeLPen(self, reg1, data):#changeLPen
        if reg1[4] == 0:#LPen is abled→disabled
            data += 8
        elif reg1[4] == 1:#LPXen is disabled→abled
            data -= 8
        lis.xfer2([self.write_reg1,data])#changeLPendata
            
    def changeFrequency(self, reg1, index_number):#change Frequency
        self.low = self.setFrequency(reg1)
        if index_number == 0:#ODR3=0,ODR2=0,ODR1=0,ODR0=1
            self.reg1_data = 0x10 + self.low
        elif index_number == 1:#ODR3=0,ODR2=0,ODR1=1,ODR0=0
            self.reg1_data = 0x20 + self.low
        elif index_number == 2:#ODR3=0,ODR2=0,ODR1=1,ODR0=1
            self.reg1_data = 0x30 + self.low
        elif index_number == 3:#ODR3=0,ODR2=1,ODR1=0,ODR0=0
            self.reg1_data = 0x40 + self.low
        elif index_number == 4:#ODR3=0,ODR2=1,ODR1=0,ODR0=1
            self.reg1_data = 0x50 + self.low
        elif index_number == 5:#ODR3=0,ODR2=1,ODR1=1,ODR0=0
            self.reg1_data = 0x60 + self.low
        elif index_number == 6:#ODR3=0,ODR2=1,ODR1=1,ODR0=1
            self.reg1_data = 0x70 + self.low
        elif index_number == 7:
            if reg1[4] == 0:#ODR3=1,ODR2=0,ODR1=0,ODR0=1
                self.reg1_data = 0x90 + self.low
            elif reg1[4] == 1:#ODR3=1,ODR2=0,ODR1=0,ODR0=0
                self.reg1_data = 0x80 + self.low
        elif index_number == 8:#ODR3=1,ODR2=0,ODR1=0,ODR0=1
            self.reg1_data = 0x90 + self.low
        lis.xfer2([self.write_reg1, self.reg1_data])#write reg1 
    
    def setFrequency(self, reg1):#reg1[4]~reg1[7]
        if reg1[4] == 0:
            if reg1[5] == 0:
                if reg1[6] == 0:
                    if reg1[7] == 0:
                        self.low = 0x00#LPen=0,Xen=0,Yen=0,Zen=0
                    elif reg1[7] == 1:
                        self.low = 0x01#LPen=0,Xen=0,Yen=0,Zen=1
                elif reg1[6] == 1:
                    if reg1[7] == 0:
                        self.low = 0x02#LPen=0,Xen=0,Yen=1,Zen=0
                    elif reg1[7] == 1:
                        self.low = 0x03#LPen=0,Xen=0,Yen=1,Zen=1
            elif reg1[5] == 1:
                if reg1[6] == 0:
                    if reg1[7] == 0:
                        self.low = 0x04#LPen=0,Xen=1,Yen=0,Zen=0
                    elif reg1[7] == 1:
                        self.low = 0x05#LPen=0,Xen=1,Yen=0,Zen=1
                elif reg1[6] == 1:
                    if reg1[7] == 0:
                        self.low = 0x06#LPen=0,Xen=1,Yen=1,Zen=0
                    elif reg1[7] == 1:
                        self.low = 0x07#LPen=0,Xen=1,Yen=1,Zen=1
        elif reg1[4] == 1:
            if reg1[5] == 0:
                if reg1[6] == 0:
                    if reg1[7] == 0:
                        self.low = 0x08#LPen=1,Xen=0,Yen=0,Zen=0
                    elif reg1[7] == 1:
                        self.low = 0x09#LPen=1,Xen=0,Yen=0,Zen=1
                elif reg1[6] == 1:
                    if reg1[7] == 0:
                        self.low = 0x0a#LPen=1,Xen=0,Yen=1,Zen=0
                    elif reg1[7] == 1:
                        self.low = 0x0b#LPen=1,Xen=0,Yen=1,Zen=1
            elif reg1[5] == 1:
                if reg1[6] == 0:
                    if reg1[7] == 0:
                        self.low = 0x0c#LPen=1,Xen=1,Yen=0,Zen=0
                    elif reg1[7] == 1:
                        self.low = 0x0d#LPen=1,Xen=1,Yen=0,Zen=1
                elif reg1[6] == 1:
                    if reg1[7] == 0:
                        self.low = 0x0e#LPen=1,Xen=1,Yen=1,Zen=0
                    elif reg1[7] == 1:
                        self.low = 0x0f#LPen=1,Xen=1,Yen=1,Zen=1
        return self.low
                               
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
        self.scale_data = self.createList(self.getScale())
        self.gravity = self.judgeSign(address)#signed data
        if self.scale_data[2] == 0:
            if self.scale_data[3] == 0:#full scale is 2g
                self.acceleration_value = self.gravity / 1024
            if self.scale_data[3] == 1:#full scale is 4g
                self.acceleration_value = self.gravity / 512
        if self.data_list[2] == 1:
            if self.scale_data[3] == 0:#full scale is 8g
                self.acceleration_value = self.gravity / 256
            if self.scale_data[3] == 1:#full scale is 16g
                self.acceleration_value = (self.gravity / (256 / 3)) 
        self.value =  round(self.acceleration_value, 2)#2 decimal places
        return self.value
    
    def search_angle(self, x_value, z_value):#get angle
        self.angle = 0
        #if data_list2[5] == 1 and data_list2[7] == 1:#flag xen and zen raised 
        if x_value != 0:#if x_value = 0 → incalculable
            self.angle = math.degrees(math.atan2(z_value, x_value))#get angle
            if self.angle < 0:#angle→(0<=angle<=359.9)
                self.angle = 360 + self.angle
        if z_value == -0.0:#angle = -0.0 = 0.0
            self.angle = 0.0
        return round(self.angle, 1)# get angle
    
    def active(self):
        self.x = self.accelerationValue(self.x_address)#get x_acceleration
        self.y = self.accelerationValue(self.y_address)#get y_acceleration
        self.z = self.accelerationValue(self.z_address)#get z_acceleration
        self.angle = self.search_angle(self.x, self.z)#get angle
        
##########################window######################
class display_lis3dh(process):
    def __init__(self, value = 0):
        super().__init__()
        self.app = QApplication(sys.argv)#system
        self.gui = QWidget()#screen
        self.x_button = QPushButton('Button', self.gui)#xbutton
        self.y_button = QPushButton('Button', self.gui)#ybutton
        self.z_button = QPushButton('Button', self.gui)#zbutton
        self.set_button = QPushButton('Button', self.gui)#setbutton
        self.finish_button = QPushButton('Button', self.gui)#finifhbutton
        self.rbutton = QRadioButton("Normalpowermode", self.gui)#radiobutton
        self.title = QLabel("加速度センサーの設定", self.gui)#title
        self.no1 = QLabel('1.測定範囲の最大値の設定', self.gui)#no1label
        self.no2 = QLabel('2.更新速度の設定', self.gui)#no2label
        self.no3 = QLabel('3.軸の有効・無効の設定', self.gui)#no3label
        self.no4 = QLabel('4.傾きの閾値の入力設定', self.gui)#no4label
        self.no5 = QLabel('5.軸の加速度データの表示', self.gui)#no5label
        self.no6 = QLabel('6.傾きの表示', self.gui)#no6label
        self.x_label = QLabel('x軸:', self.gui)#xlabel
        self.y_label = QLabel('y軸:', self.gui)#ylabel
        self.z_label = QLabel('z軸:', self.gui)#zlabel
        self.x_value = QLabel('', self.gui)#display xvalue
        self.y_value = QLabel('', self.gui)#display yvalue
        self.z_value = QLabel('', self.gui)#display zvalue
        self.degree = QLabel('傾き:', self.gui)#degreelabel
        self.degree_value = QLabel('', self.gui)#display degree
        #self.scale = QLabel('', self.gui)
        self.textBox = QLineEdit(self.gui)#input data
        self.comboBox = QComboBox(self.gui)#create combobox
        self.comboBox.addItem("full scale is +/-2g")#item1
        self.comboBox.addItem("full scale is +/-4g")#item2
        self.comboBox.addItem("full scale is +/-8g")#item3
        self.comboBox.addItem("full scale is +/-16g")#item4
        self.comboBox.setCurrentIndex(0)#default combobox.index
        self.speedCombo = QComboBox(self.gui)#speedCombo

    def window(self):#create window
        self.gui.setWindowTitle('3軸加速度センサー')
        self.gui.setGeometry(10,20,800,700)
        self.gui.setStyleSheet("background:white")

    def Label(self):#create label
        self.window()#window
        self.title.move(200, 0)#setting title
        self.title.setStyleSheet("font-size:20pt;font-weight:bold;color:magenta;background-color:white;")
        self.title.resize(350, 50)
        self.title.setAlignment(Qt.AlignCenter)
        self.no1.move(0, 50)#setting no1
        self.no1.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.no1.resize(400, 30)    
        self.no2.move(0, 155)#setting no2
        self.no2.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.no2.resize(400, 30)   
        self.no3.move(0, 260)#setting no3
        self.no3.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.no3.resize(400, 30)    
        self.no4.move(0, 365)#setting no4
        self.no4.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.no4.resize(400, 30)    
        self.no5.move(0, 470)#setting no5
        self.no5.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.no5.resize(400, 30)   
        self.no6.move(0, 575)#setting no6
        self.no6.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.no6.resize(400, 30)  
        self.x_label.move(0, 525)#setting xlabel
        self.x_label.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.x_label.resize(50, 30) 
        self.x_value.move(50, 525)#setting xvalue
        self.x_value.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.x_value.resize(100, 30)       
        self.y_label.move(250, 525)#setting ylabel
        self.y_label.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.y_label.resize(50, 30)    
        self.y_value.move(300, 525)#setting yvalue
        self.y_value.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white")
        self.y_value.resize(100, 30)       
        self.z_label.move(500, 525)#setting zlabel
        self.z_label.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.z_label.resize(50, 30)      
        self.z_value.move(550, 525)#setting zvalue
        self.z_value.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.z_value.resize(100, 30)
        self.timerJob()#get timerJob information
        self.degree.move(250, 630)#setting degreelabel
        self.degree.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.degree.resize(50, 30)
        self.degree_value.move(300, 630)#setting degreevalue
        self.degree_value.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.degree_value.resize(100, 30)
    
    def timerJob(self):#set timerJob
        self.time = QTimer(self.gui)#set time
        self.time.timeout.connect(self.displayValue)#active display value
        self.time.start(1000)#1 seconds
    
    def displayValue(self):#display screen
        global x#global x, y, z, angle, get_axis
        global y
        global z
        global angle
        global get_axis
        self.get_axis = super().getAxis()#getaxis
        self.axis_list = super().createList(self.get_axis)#getaxis→axislist
        super().active()#get x_value,y_value,z_value,angle
        if self.axis_list[7] == 1:#X axis abled
            self.x_value.setText(str('{:.02f}'.format(self.x)) + "  g")
        elif self.axis_list[7] == 0:#X axis disabled
            self.x_value.setText("None")
        if self.axis_list[6] == 1:#Y axis abled
            self.y_value.setText(str('{:.02f}'.format(self.y)) + "  g")
        elif self.axis_list[6] == 0:#Y axis disabled
            self.y_value.setText("None")
        if self.axis_list[5] == 1:#Z axis abled
            self.z_value.setText(str('{:.02f}'.format(self.z)) + "  g")
        elif self.axis_list[5] == 0:#Z axis disabled
            self.z_value.setText("None")
        if self.axis_list[5] == 1 and self.axis_list[7] == 1:#X axis and Z axis abled
            self.degree_value.setText(str('{:.01f}'.format(self.angle)) + "度")
        else:#X axis or Z axis disabled
            self.degree_value.setText("None")
    
    def finishButton(self):#fiinish
        global finish_button#push finish_button
        #finish system and create popup
        self.reply = QMessageBox.question(self.gui, "確認", "Question", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
        if self.reply == QMessageBox.Yes:
            sys.exit(self.app.exec_())

    def xButton(self):#xbutton
        global x_button#push x_button
        global get_axis#global get_axis
        self.get_axis = super().getAxis()#get axis
        self.axis_list = super().createList(self.get_axis)#getaxis→axislist
        self.input_x = self.x_button.text()#get x_button text
        super().changeXen(self.axis_list, self.get_axis)#change Xen
        if self.input_x == "x軸は有効":#change text
            self.x_button.setText("x軸は無効")
        else:#change text
            self.x_button.setText("x軸は有効")

    def yButton(self):#ybutton
        global y_button#push y_button
        global get_axis#global get_axis
        self.get_axis = super().getAxis()#getaxis
        self.axis_list = super().createList(self.get_axis)#getaxis→axislist
        self.input_y = self.y_button.text()#get y_button text
        super().changeYen(self.axis_list, self.get_axis)#change Yen
        if self.input_y == "y軸は有効":#change text
            self.y_button.setText("y軸は無効")
        else:#change text
            self.y_button.setText("y軸は有効")

    def zButton(self):#zbutton
        global z_button#push z_button
        global get_axis#global get_axis
        self.get_axis = super().getAxis()#getaxis
        self.axis_list = super().createList(self.get_axis)#getaxis→axislist
        self.input_z = self.z_button.text()#get z_button text
        super().changeZen(self.axis_list, self.get_axis)#change Zen
        if self.input_z == "z軸は有効":#change text
            self.z_button.setText("z軸は無効")
        else:#change text
            self.z_button.setText("z軸は有効")
    
    def setButton(self):#setbutton
        global set_button#push set_button
        global angle#global angle
        global get_axis#global get_axis
        self.get_axis = super().getAxis()#getaxis
        self.axis_list = super().createList(self.get_axis)#getaxis→axislist
        self.input_data = self.textBox.text()#get textBox text
        super().active()#get x_value,y_value,z_value,angle
        if int(self.input_data) < self.angle:#input_data < angle
            self.textBox.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:red;")
        elif int(self.input_data) >= self.angle or self.degree_value.text() == "None":#input_data >= angle
            self.textBox.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")

    def Button(self):#button
        self.Label()#label
        self.finish_button.move(650, 0)#setting finish_button
        self.finish_button.setText('システム終了')
        self.finish_button.setStyleSheet("font-size:15pt;font-weight:bold;color:black;background-color:red;")
        self.finish_button.resize(150, 50)
        self.finish_button.clicked.connect(self.finishButton)#finishButton event
        self.x_button.move(0, 300)#setting x_button
        self.x_button.setText('x軸は有効')
        self.x_button.setStyleSheet("font-size:15pt;font-weight:bold;color:black;background-color:cyan;")
        self.x_button.resize(200, 50)
        self.x_button.clicked.connect(self.xButton)#xButton event
        self.y_button.move(250, 300)#setting y_button
        self.y_button.setText('y軸は有効')
        self.y_button.setStyleSheet("font-size:15pt;font-weight:bold;color:black;background-color:cyan;")
        self.y_button.resize(200, 50)
        self.y_button.clicked.connect(self.yButton)#yButton event
        self.z_button.move(500, 300)#setting z_button
        self.z_button.setText('z軸は有効')
        self.z_button.setStyleSheet("font-size:15pt;font-weight:bold;color:black;background-color:cyan;")
        self.z_button.resize(200, 50)
        self.z_button.clicked.connect(self.zButton)#zButton event
        self.set_button.move(450, 410)#setting set_button
        self.set_button.setText('設定完了')
        self.set_button.setStyleSheet("font-size:15pt;font-weight:bold;color:black;background-color:cyan;")
        self.set_button.resize(100, 50)
        self.set_button.clicked.connect(self.setButton)#setButton event

    def normal_speed(self):#normalpowermode
        self.speedCombo.addItem("frequency is 1Hz")#speedCombo addItems
        self.speedCombo.addItem("frequency is 10Hz")
        self.speedCombo.addItem("frequency is 25Hz")
        self.speedCombo.addItem("frequency is 50Hz")
        self.speedCombo.addItem("frequency is 100Hz")
        self.speedCombo.addItem("frequency is 200Hz")
        self.speedCombo.addItem("frequency is 400Hz")
        self.speedCombo.addItem("frequency is 1.25kHz")
    
    def low_speed(self):#lowpowermode
        self.speedCombo.addItem("frequency is 1Hz")#speedCombo addItems
        self.speedCombo.addItem("frequency is 10Hz")
        self.speedCombo.addItem("frequency is 25Hz")
        self.speedCombo.addItem("frequency is 50Hz")
        self.speedCombo.addItem("frequency is 100Hz")
        self.speedCombo.addItem("frequency is 200Hz")
        self.speedCombo.addItem("frequency is 400Hz")
        self.speedCombo.addItem("frequency is 1.6kHz")
        self.speedCombo.addItem("frequency is 5kHz")

    def Combo(self):#combobox
        self.Button()#button
        self.comboBox.move(250,100)#setting comboBox
        self.comboBox.setStyleSheet("font-size:10pt;font-weight:normal;color:black;background-color:yellow;")
        self.comboBox.resize(200,50)
        self.comboBox.activated[str].connect(self.selected)#comboBox event
        self.normal_speed()#comboBox addItems normal_speed()
        self.speedCombo.move(250, 200)#setting speedCombo
        self.speedCombo.setStyleSheet("font-size:10pt;font-weight:normal;color:black;background-color:yellow;")
        self.speedCombo.resize(200,50)
        self.speedCombo.activated[str].connect(self.selected2)#speedCombo event
        
    def selected(self):#comboBox event
        self.index = self.comboBox.currentIndex()#get comboBox index
        super().changeScale(self.index)#change scale
        
    def selected2(self):#speedCombo event
        global get_axis#global get_axis
        self.index = self.speedCombo.currentIndex()#get speedCombo index
        self.get_axis = super().getAxis()#get axis
        self.axis_list = super().createList(self.get_axis)#getaxis→axislist
        super().changeFrequency(self.axis_list, self.index)#chagne frequency

    def Text(self):#textbox
        self.Combo()#combo
        self.textBox.move(250, 410)#setting textbox
        self.v = QIntValidator(0, 999)#limit int(0~999)
        self.textBox.setValidator(self.v)#limit intvalue
        self.textBox.setStyleSheet("font-size:15pt;font-weight:normal;color:black;background-color:white;")
        self.textBox.resize(200, 50)
        self.textBox.setText("")

    def toggleRadio(self):#radioボックス処理
        global get_axis#global get_axis
        self.get_axis = super().getAxis()#get axis
        self.axis_list = super().createList(self.get_axis)#get_axis→axis_list
        super().changeLPen(self.axis_list, self.get_axis)#changeLPen
        if self.rbutton.isChecked() == True:#check rbutton
            self.speedCombo.clear()#normal_spped clear
            self.low_speed()#addItems low_speed
            self.rbutton.setText("Lowpowermode")#change text
        else:
            self.speedCombo.clear()#low_speed clear
            self.normal_speed()#addItems normal_speed
            self.rbutton.setText("Normalpowermode")#change text
        #index of normal→index0 of low,index of low→index0 of normal
        self.selected2()
            
    def radio(self):#radioBox
        self.Text()#text
        self.rbutton.move(0, 210)#setting rbutton
        self.rbutton.resize(200, 30)
        self.rbutton.toggled.connect(self.toggleRadio)#toggleRadio event

    def active(self):#active event
        self.gui.show()#display window
        sys.exit(self.app.exec_())#finish system

process = process()#class process
process.setLis3dh()#set reg1, reg4
lis3dh = display_lis3dh()#class display_lis3dh
lis3dh.radio()#active winodw process
lis3dh.active()#display window and finishsystem

lis.close()#finish spi