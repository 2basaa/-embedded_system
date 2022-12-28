import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

mcp3002_pin = 7#MCP3002
lis3dh_pin = 8#LIS3DH
sdo = 9#SDO
sdi =10#SDI
sclk = 11#SPIO SCLK
set_out = [mcp3002_pin, lis3dh_pin, sdi, sclk]
#lis3dh=0xcf, mcp3002=0x68
GPIO.setup(set_out, GPIO.OUT)#output
GPIO.setup(sdo, GPIO.IN)#9=SDO

class lis3dh:#setting lis3dh 
    def __init__(self, sdo = 9, sdi = 10, sclk = 11):
        self.sdo = sdo#set sdo
        self.sdi = sdi#set sdi
        self.sclk = sclk#set sclk

    def spi_transport_start(self, cs):
       self.cs = cs#set cs
       GPIO.output(self.cs, GPIO.HIGH)##SPI enabled
       GPIO.output(self.sclk, GPIO.HIGH)#SPC
       GPIO.output(self.sdi, GPIO.HIGH)#SDI
       #GPIO.input(9)
       time.sleep(0.01)
       #start read or write before set preparation
       GPIO.output(self.cs, GPIO.LOW)#start transport
       GPIO.output(self.sclk, GPIO.LOW)#SPC
       GPIO.output(self.sdi, GPIO.LOW)

    def create_lis3dh_command(self):#create lis3dh command = 0b11001111
        time.sleep(0.01)
        GPIO.output(self.sdi, GPIO.HIGH)#bit7=1
        GPIO.output(self.sclk, GPIO.HIGH)
        time.sleep(0.01)
        for self.num in range(7):#create bit6~bit0 "HIGH" or "LOW"
            GPIO.output(self.sclk, GPIO.LOW)#change data
            if self.num == 0 or self.num == 3 or self.num == 4 or self.num == 5 or self.num == 6:
                GPIO.output(self.sdi, GPIO.HIGH)#bitn = 1
            else:
                GPIO.output(self.sdi, GPIO.LOW)#bitn = 0
            time.sleep(0.01)
            GPIO.output(self.sclk, GPIO.HIGH)#read data
            time.sleep(0.01)

    def spi_read_protocol(self):#0b00110011
        time.sleep(0.01)
        self.switch = 0 #set switch
        self.read_data = []#get acceraretion data
        for self.num in range(8):
            GPIO.output(self.sclk, GPIO.LOW)
            if GPIO.input(self.sdo) == GPIO.HIGH:
                self.switch = 1
            elif GPIO.input(self.sdo) == GPIO.LOW:
                self.switch = 0
            self.read_data.append(self.switch)#get bit of acceraration_data
            time.sleep(0.01)
            GPIO.output(self.sclk, GPIO.HIGH)#read bit
            time.sleep(0.01)
        return self.read_data#get data of rcv[1]
    
    def binary_to_decimal(self, data):#binary→decimal
        self.decimal_data = 0 #for print decimal_data
        self.data = data#binary data
        #data = (data of lis3dh) or (data of mcp3002)
        for self.num in range(8):#binary→decimal
            self.decimal_data += data[self.num] * pow(2, 7 -self.num)
        print(self.decimal_data)

    def stop_read_protocol(self, cs):
        GPIO.output(self.cs, GPIO.HIGH)#finish transport data    


class mcp3002(lis3dh):#setting mcp3002
    def __init__(self, sdo = 9, sdi = 10, sclk = 11):#set sdo, sdi , sclk
        super().__init__(sdo = 9, sdi = 10, sclk = 11)
    
    def spi_transport_start(self, cs):#set starting transport
        super().spi_transport_start(cs)
    
    def create_mcp3002_command(self):#0b01101
        time.sleep(0.01)
        GPIO.output(self.sclk, GPIO.HIGH)#bit7 = 0
        time.sleep(0.01)
        for self.number in range(4):
            GPIO.output(self.sclk, GPIO.LOW)#change data
            if self.number == 2:#(bit4 = ODD/SIGN)= 0
                GPIO.output(self.sdi, GPIO.LOW)
            else:#(bit6=start and bit5=SGL/DFF and bit3=MSBF) = 1
                GPIO.output(self.sdi, GPIO.HIGH)
            time.sleep(0.01)
            GPIO.output(self.sclk, GPIO.HIGH)#read data
            time.sleep(0.01)
        
    def read_temperature(self):
        GPIO.output(self.sclk, GPIO.LOW)#change data
        GPIO.output(self.sdi, GPIO.LOW)#mcp3002_command = 0x68
        #GPIO9 = null bit
        time.sleep(0.01)
        GPIO.output(self.sclk, GPIO.HIGH)#read data
        time.sleep(0.01)
        for self.number in range(2):# create GPIO9 B9 and B8
            GPIO.output(self.sclk, GPIO.LOW)#change data
            time.sleep(0.01)
            GPIO.output(self.sclk, GPIO.HIGH)#read data
            time.sleep(0.01)
        self.switch = 0# temperature of rcv[1]
        self.mcp3002_list = []
        for self.num in range(8):#GPIO B7 ~ B0
            GPIO.output(self.sclk, GPIO.LOW)
            if GPIO.input(self.sdo) == GPIO.HIGH:
                self.switch = 1#high
            elif GPIO.input(self.sdo) == GPIO.LOW:
                self.switch = 0#low
            self.mcp3002_list.append(self.switch)#bitn of temperature data
            time.sleep(0.01)
            GPIO.output(self.sclk, GPIO.HIGH)#read bit
            time.sleep(0.01)
        return self.mcp3002_list#get data of rcv[1]
    
    def binary_to_decimal(self, data):#binary→decimal
        super().binary_to_decimal(data)
        
    def stop_read_protocol(self, cs):#finish transport data
        super().stop_read_protocol(cs)


def homework1():#lis3dh
    lis = lis3dh()#instantiate a class
    lis.spi_transport_start(lis3dh_pin)#start transport
    lis.create_lis3dh_command()#lis3dh_command 0xcf
    lis3dh_data = lis.spi_read_protocol()#get data from sdo
    lis.binary_to_decimal(lis3dh_data)#binary→decimal
    lis.stop_read_protocol(lis3dh_pin)#finish transport
    time.sleep(1)

def homework2():#mcp3002
    mcp = mcp3002()#instantiate a class
    mcp.spi_transport_start(mcp3002_pin)#start transport
    mcp.create_mcp3002_command()#create command mcp3002
    mcp3002_data = mcp.read_temperature()#get data from sdo
    mcp.binary_to_decimal(mcp3002_data)#binary→deximal
    mcp.stop_read_protocol(mcp3002_pin)#finish transport
    time.sleep(1)

try:
    while True:
        #homework1()
        homework2()
        
except KeyboardInterrupt:
    pass

GPIO.cleanup()