#!/usr/bin/python

import cgi, cgitb
import spidev

cgitb.enable()

lis = spidev.SpiDev()
lis.open(0,0)#SPIO CE0
lis.max_speed_hz = 10000#maxspeed 10000Hz
lis.bits_per_word=8#1word = 8bit

###############process##########
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
        self.decimal_data = 0 #decimal_data
    
    def defaultStatus(self):
        lis.xfer2([self.write_reg1,0x17])#1Hz,(x,y,z) abled
        lis.xfer2([self.write_reg4,0x00])#2g

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
    
    def createDecimal(self, data_list):#binary to decimal
        self.decimal_data = 0
        for self.num in range(8):#get decimal_data
            self.decimal_data += pow(2, 7- self.num) * data_list[self.num]
        return self.decimal_data
    
    def getReg1(self):#get reg1_status
        self.reg1 = lis.xfer2([self.read_reg1,0x00])
        return self.reg1[1]

    def getScale(self):#get reg4_status
        self.reg4 = lis.xfer2([self.read_reg4,0x00])
        return self.reg4[1]

    def changeScale(self, index_number):#change range of scale
        if index_number == 2:
            lis.xfer2([self.write_reg4,0x00])#scale is 2g
        elif index_number == 4:
            lis.xfer2([self.write_reg4,0x10])#scale is 4g
        elif index_number == 8:
            lis.xfer2([self.write_reg4,0x20])#scale is 8g
    
    def changeXen(self, reg1, sign):#change Xen
        if sign == 1:#Xen is abled→disabled
            reg1[7] = 1
        elif sign == 0:#Xen is disabled→abled
            reg1[7] = 0
        self.decimal_data = self.createDecimal(reg1)
        lis.xfer2([self.write_reg1,self.decimal_data])#changeXendata
        
    def changeYen(self, reg1, sign):#change Yen
        if sign == 1:#Yen is abled→disabled
            reg1[6] = 1
        elif sign == 0:#Yen is disabled→abled
            reg1[6] = 0
        #print(hex(data))
        self.decimal_data = self.createDecimal(reg1)
        lis.xfer2([self.write_reg1,self.decimal_data])#changeYendata   
    
    def changeZen(self, reg1, sign):#changeZen
        if sign == 1:#Zen is abled→disabled
            reg1[5] = 1
        elif sign == 0:#Zen is disabled→abled
            reg1[5] = 0
        #print(hex(data))
        self.decimal_data = self.createDecimal(reg1)
        lis.xfer2([self.write_reg1,self.decimal_data])#changeZendata

    def changeFrequency(self, reg1, index_number):#change Frequency
        self.low = self.setFrequency(reg1)
        if index_number == 1:#ODR3=0,ODR2=0,ODR1=0,ODR0=1
            self.reg1_data = 0x10 + self.low#1Hz
        elif index_number == 10:#ODR3=0,ODR2=0,ODR1=1,ODR0=0
            self.reg1_data = 0x20 + self.low#10Hz
        elif index_number == 25:#ODR3=0,ODR2=0,ODR1=1,ODR0=1
            self.reg1_data = 0x30 + self.low#25Hz
        lis.xfer2([self.write_reg1, self.reg1_data])#write reg1
  
    def setFrequency(self, reg1):#reg1[4]~reg1[7]
        if reg1[5] == 0:
            if reg1[6] == 0:
                if reg1[7] == 0:
                    self.low = 0x00#Xen=0,Yen=0,Zen=0
                elif reg1[7] == 1:
                    self.low = 0x01#Xen=0,Yen=0,Zen=1
            elif reg1[6] == 1:
                if reg1[7] == 0:
                    self.low = 0x02#Xen=0,Yen=1,Zen=0
                elif reg1[7] == 1:
                    self.low = 0x03#Xen=0,Yen=1,Zen=1
        elif reg1[5] == 1:
            if reg1[6] == 0:
                if reg1[7] == 0:
                    self.low = 0x04#Xen=1,Yen=0,Zen=0
                elif reg1[7] == 1:
                    self.low = 0x05#Xen=1,Yen=0,Zen=1
            elif reg1[6] == 1:
                if reg1[7] == 0:
                    self.low = 0x06#Xen=1,Yen=1,Zen=0
                elif reg1[7] == 1:
                    self.low = 0x07#Xen=1,Yen=1,Zen=1
        return self.low
    
    def readlis3dh(self, address):#get lis3dhdata
        self.rcv = lis.xfer2([address,0x00])#get high_data
        self.g = self.rcv[1]
        self.rcv = lis.xfer2([address+1,0x00])#get_low_data
        self.g = (self.g | self.rcv[1]<<8)>>4#12bit
        if self.g >= 2048:
            self.g -= 4096
        self.scale_data = self.createList(self.getScale())
        if self.scale_data[2] == 0:
            if self.scale_data[3] == 0:
                self.value = self.g / 1024
            elif self.scale_data[3] == 1:
                self.value = self.g /512
        elif self.scale_data[2] == 1:
            self.value = self.g /256
        return self.value

    def active(self):#active range
        self.x = self.readlis3dh(self.x_address)#get x_acceleration
        self.y = self.readlis3dh(self.y_address)#get y_acceleration
        self.z = self.readlis3dh(self.z_address)#get z_acceleration
        return self.x, self.y, self.z

####################active range######################
form = cgi.FieldStorage()#get form from link

process = process()
#process.defaultStatus()#set defalutstatus
####################setLIS3dh#######################
def setLIS():
    #################frequency#############
    if "frequency" not in form:#not frequency form
        process.getReg1()
    elif "frequency" in form:
        if str(form['frequency'].value) == "1":#1Hz
            process.changeFrequency(process.createList(process.getReg1()), 1)
        elif str(form['frequency'].value) == "10":#10Hz
            process.changeFrequency(process.createList(process.getReg1()), 10)
        elif str(form['frequency'].value) == "25":#25Hz
            process.changeFrequency(process.createList(process.getReg1()), 25)
    ################xvalue############
    if "xvalue" not in form:#not xvalue form
        process.getReg1()
    else:
        if str(form['xvalue'].value) == "1":#xaxis abled
            process.changeXen(process.createList(process.getReg1()), 1)
        elif str(form['xvalue'].value) == "0":#xaxis disabled
            process.changeXen(process.createList(process.getReg1()), 0)
    #################yvalue##############
    if "yvalue" not in form:#not yvalue form
        process.getReg1()
    else:
        if str(form['yvalue'].value) == "1":#yaxis abled
            process.changeYen(process.createList(process.getReg1()), 1)
        elif str(form['yvalue'].value) == "0":#yaxis disabled
            process.changeYen(process.createList(process.getReg1()), 0)
    #################zvalue################
    if "zvalue" not in form:#not zvalue form
        process.getReg1()
    else:
        if str(form['zvalue'].value) == "1":#zaxis abled
            process.changeZen(process.createList(process.getReg1()), 1)
        elif str(form['zvalue'].value) == "0":#zaxis disabled
            process.changeZen(process.createList(process.getReg1()), 0)
    #################scale################
    if "scale" not in form:#not scale form
        process.getReg1()
    else:
        if str(form['scale'].value) == "2g":#scale is 2g
            process.changeScale(2)
        elif str(form['scale'].value) == "4g":#scale is 4g
            process.changeScale(4)
        elif str(form['scale'].value) == "8g":#scale is 8g
            process.changeScale(8)

if "Reset" not in form:#not Reset form
    setLIS()
elif str(form['Reset'].value) == "0":#Reset is 0
    setLIS()
elif str(form['Reset'].value) == "1":#Reset is 1
    process.defaultStatus()

#################display##########################
x, y, z= process.active()#get data
print("Content-Type: text/xml\n")#xml format
print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
print("<data>\n<x>%s</x>\n<y>%s</y>\n<z>%s</z>\n</data>" % 
(x,y,z))#get data of x&y&z