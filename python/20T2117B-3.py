import smbus
import time
import curses

i2c = smbus.SMBus(1)
address = 0x48#address of ADT7410

screen = curses.initscr()#screen initialization
curses.noecho()#do not print letter in screen
curses.cbreak()#don't wait enter key
screen.nodelay(1)#display letter in screen
screen.addstr('start\n\r')#move to cursor 0row 0column

def set_bitmode():#set 16bit temperature
    i2c.write_byte_data(address,0x03, 0x80)#register address 0x03 set 0x80→measure 16bit

def read_adt7410(address1, address2):#read decimal temperature
    byte_data = i2c.read_byte_data(address, address1)#(0x48, 0x00)
    data = byte_data << 8 #leftshift
    byte_data = i2c.read_byte_data(address, address2)#(0x48, 0x01)
    data = data | byte_data #data + bytedata(16bit)
    if data < 32768:#positive temperature
        data = (data) / 128 #10decimal temperature of 16bit
    elif data >= 32768:#negative temperature
        data = (data - 65536) / 128 #10decimal temperature of 16bit
    return data

def set_THYST():#set THYST
    i2c.write_byte_data(address, 0x0A, 0x00)#address is 0x0A and bit 0x00

def set_THIGH():#set THIGH = 30 degree, msb address is 0x04, lsb address is 0x05
    i2c.write_byte_data(address, 0x04, 0x0D)#MSB = 0b00001101 = 26degree
    i2c.write_byte_data(address, 0x05, 0x00)#LSB = 0x00
    
def set_TLOW():#set 28 degree, msb address is 0x06, lsb address is 0x07
    i2c.write_byte_data(address, 0x06, 0x0C)#MSB = 0b00001100 = 24degree
    i2c.write_byte_data(address, 0x07, 0x00)#LSB = 0x00

def get_THYST():#get THYST degree
    thyst = i2c.read_byte_data(address, 0x0A)# get tempreture of thyst
    return thyst
    
def get_THIGH():#get THIGH degree
    thigh = read_adt7410(0x04, 0x05)# get tempreture of thigh
    thyst = get_THYST()# get tempreture of thyst
    thigh = thigh - thyst # thigh = (thigh=30)-thyst(thyst=0) 
    return thigh

def get_TLOW():#get TLOW degree
    tlow = read_adt7410(0x06, 0x07)# get tempreture of tlow
    thyst = get_THYST()# get tempreture of thyst
    tlow = tlow + thyst# tlow = (tlow=28)-thyst(thyst=0) 
    return tlow

def set_keyboard():#set keyboard operation
    keyInput = screen.getch() #get keystrokes as ASCII digits
    degree = 0 #set degree
    if keyInput == ord('r'):#if get letter'r' from keyboard 
        degree = read_adt7410(0x00, 0x01)#get room temperature
        thigh = get_THIGH()#get temperature(26 degree) = thigh - thyst
        tlow = get_TLOW()#get temperature(24degree) = tlow + thyst
        if degree >= thigh:#degree >= thigh
            screen.addstr("current temperature is over 26 degrees\n\r")#display screen
        if degree <= tlow:#degree <= tlow
            screen.addstr("current temperature is under 24 degrees\n\r")#display screen
        screen.addstr("room temperature is " + str(degree) + "\n\r")#display screen
        i2c.write_byte_data(address,0x03, 0xE0)#shutdownmode
    if keyInput >= 0:#typed from the keyboard
        if keyInput != ord('r'): #if do not get letter'r' from keyboard 
            screen.addstr(chr(keyInput) + "\n\r")#display screen
            screen.addstr('Press r to output the temperature\n\r')#display screen
    if keyInput < 0:#not type from keyboard amd to prevent errors
        screen.addstr(0,0,'no key \n\r')#write to row 0 column 0→ 'no key'
    return degree
        
try:
    while True:
        set_bitmode()#13bit→16bit
        set_THYST()#THYST = 0 degree
        set_THIGH()#THIGH = 26 degree
        set_TLOW()#TLOW = 24 degree
        set_keyboard()#input keyboard
        time.sleep(1)
   
except KeyboardInterrupt:
    pass

curses.nocbreak()#unset curses.echo()
curses.echo()#unset curses.noeco()
curses.endwin()#finish process