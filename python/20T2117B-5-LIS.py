import spidev
import time
import math
import curses

screen = curses.initscr()#screen initialization
curses.noecho()#do not print letter in screen
curses.cbreak()#don't wait enter key
screen.nodelay(1)#display letter in screen
screen.addstr('start\n\r')#move to cursor 0row 0column

lis = spidev.SpiDev()
lisread = 0x80#read mode
liswrite = 0x00#write mode
lissingle = 0x00#MSbit = 0
lismulti = 0x40#MSbit = 1

ctrl_reg1 = 0x20#set axis and set odr
ctrl_reg4 = 0x23#set full scale selection
status_reg = 0x27#status axis

x_address = 0x28
y_address = 0x2a
z_address = 0x2c

def set_lis3dh():#set lis3dh
    lis.open(0,0)#SPIO CE0
    lis.max_speed_hz = 10000
    lis.bits_per_word=8#1word = 8bit
    #↓appdate_data 1 second
    lis.xfer2([ liswrite| lissingle | ctrl_reg1,0x17])#1hz
    lis.xfer2([ liswrite| lissingle | ctrl_reg4,0x00])#scale is 2g

def create_list(data):#create 8bit of list
    data_list = []#create list
    quotient = 0
    i = 7
    for num in range(8):
        quotient = data // pow(2, i)#create data_list[0]~data_list[7]
        if data >= pow(2, i):#data >= 2^i
            data -= pow(2, i)#data - 2^i
        data_list.append(quotient)#append quotient
        i -= 1
    return data_list #get data_list
 
def get_scale():#get information of ctrl_reg4 
    reg4 = lis.xfer2([lisread | lissingle | ctrl_reg4,0x00])
    return reg4[1]#get information of ctrl_reg4

def get_axis():#get information of ctrl_reg1
    reg1 = lis.xfer2([lisread | lissingle | ctrl_reg1,0x00])
    return reg1[1]#get information of ctrl_reg1

def change_xen(data):#set ctrl_reg1
    #change xen(0→1)
    if data[7] == 0:#xen
        if data[6] == 0:#yen
            if data[5] == 0:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x11])
                screen.addstr('y-axis and z-axis are disabled,x-axis is enabled\n\r')
            elif data[5] == 1:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x15])
                screen.addstr('y-axis is disabled,x-axis and z-axis are enabled\n\r')
        elif data[6] == 1:#yen
            if data[5] == 0:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x13])
                screen.addstr('z-axis is disabled,x-axis and y-axis is enabled\n\r')
            elif data[5] == 1:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x17])
                screen.addstr('x-, y-, and z-axes are enabled\n\r')
    #change xen(1→0)
    elif data[7] == 1:#xen
        if data[6] == 0:#yen
            if data[5] == 0:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x10])
                screen.addstr('x-, y-, and z-axes are disabled\n\r')
            elif data[5] == 1:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x14])
                screen.addstr('x-axis and y-axis are disabled,z-axis is enabled\n\r')
        elif data[6] == 1:#yen
            if data[5] == 0:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x12])
                screen.addstr('x-axis and z-axis are disabled,y-axis is enabled\n\r')
            elif data[5] == 1:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x16])
                screen.addstr('x-axis is disabled,y-axis and z-axis are enabled\n\r')

def change_yen(data):#set ctrl_reg1
    #change yen(0→1)
    if data[6] == 0:#yen
        if data[7] == 0:#yen
            if data[5] == 0:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x12])
                screen.addstr('x-axis and z-axis are disabled,y-axis is enabled\n\r')
            elif data[5] == 1:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x16])
                screen.addstr('x-axis is disabled,y-axis and z-axis are enabled\n\r')
        elif data[7] == 1:#yen
            if data[5] == 0:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x13])
                screen.addstr('z-axis is disabled,x-axis and y-axis is enabled\n\r')
            elif data[5] == 1:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x17])
                screen.addstr('x-, y-, and z-axes are enabled\n\r')
    #change yen(1→0)
    elif data[6] == 1:#yen
        if data[7] == 0:#xen
            if data[5] == 0:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x10])
                screen.addstr('x-, y-, and z-axes are disabled\n\r')
            elif data[5] == 1:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x14])
                screen.addstr('x-axis and y-axis are disabled,z-axis is enabled\n\r')
        elif data[7] == 1:#xen
            if data[5] == 0:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x11])
                screen.addstr('y-axis and z-axis are disabled,x-axis is enabled\n\r')
            elif data[5] == 1:#zen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x15])
                screen.addstr('y-axis is disabled,x-axis and z-axis are enabled\n\r')

def change_zen(data):#set ctrl_reg1
    #change zen(0→1)
    if data[5] == 0:#zen
        if data[6] == 0:#yen
            if data[7] == 0:#xen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x14])
                screen.addstr('x-axis and y-axis are disabled,z-axis is enabled\n\r')
            elif data[7] == 1:#xen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x15])
                screen.addstr('y-axis is disabled,x-axis and z-axis are enabled\n\r')
        elif data[6] == 1:#yen
            if data[7] == 0:#xen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x16])
                screen.addstr('x-axis is disabled,y-axis and z-axis is enabled\n\r')
            elif data[7] == 1:#xen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x17])
                screen.addstr('x-, y-, and z-axes are enabled\n\r')
    #change zen(1→0)
    elif data[5] == 1:#zen
        if data[6] == 0:#yen
            if data[7] == 0:#xen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x10])
                screen.addstr('x-, y-, and z-axes are disabled\n\r')
            elif data[7] == 1:#xen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x11])
                screen.addstr('y-axis and z-axis are disabled,x-axis is enabled\n\r')
        elif data[6] == 1:#yen
            if data[7] == 0:#xen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x12])
                screen.addstr('x-axis and z-axis are disabled,y-axis is enabled\n\r')
            elif data[7] == 1:#xen
                lis.xfer2([liswrite | lissingle | ctrl_reg1,0x13])
                screen.addstr('z-axis is disabled,x-axis and y-axis are enabled\n\r')

def set_key(data):#set keyboard operation
    keyInput = screen.getch() #get keystrokes as ASCII digits
    if keyInput == ord('2'):#if get letter'2' from keyboard
        lis.xfer2([liswrite | lissingle |ctrl_reg4,0x00])#scale 2g
        screen.addstr("full scale is 2g\n\r")
    if keyInput == ord('4'):#if get letter'4' from keyboard
        lis.xfer2([liswrite | lissingle |ctrl_reg4,0x10])#scale 4g
        screen.addstr("full scale is 4g\n\r")
    if keyInput == ord('x'):#if get letter'x' from keyboard
        change_xen(data)#change xen
    if keyInput == ord('y'):#if get letter'y' from keyboard
        change_yen(data)#change yen
    if keyInput == ord('z'):#if get letter'z' from keyboard
        change_zen(data)#cahnge zen
    axis = lis.xfer2([lisread | lissingle |ctrl_reg1,0x00])#get information of axis
    scale = lis.xfer2([lisread | lissingle |ctrl_reg4,0x00])#get information of scale
    return axis[1], scale[1]

def readlis3dh(reg2):#get lis3dhdata
    rcv = lis.xfer2([lisread | lissingle |reg2,0x00])#get high_data
    g = rcv[1]
    rcv = lis.xfer2([lisread | lissingle |reg2+1,0x00])#get_low_data
    g = (g | rcv[1]<<8)>>4#12bit
    return g#get sensor_data

def judge_sign(address):#cahnge sign
    judge_sign = readlis3dh(address)#get sensor data
    if judge_sign >= 2048:#minus
        judge_sign -= 4096
    else:#plus
        judge_sign = judge_sign  
    return judge_sign#get signed data

def acceleration_value(address, data_list):#set acceleration
    gravity = judge_sign(address)#signed data
    if data_list[3] == 0:
        acceleration_value = gravity / 1024
    if data_list[3] == 1:
        acceleration_value = gravity / 512
    value =  round(acceleration_value, 2)#2 decimal places
    return value

def search_angle(address1, address2, data_list, data_list2):#get angle
    x_value = acceleration_value(address1, data_list)#x_value
    z_value = acceleration_value(address2, data_list)#z_value
    angle = 0
    if data_list2[5] == 1 and data_list2[7] == 1:#flag xen and zen raised 
        if x_value != 0:#if x_value = 0 → incalculable
            angle = math.degrees(math.atan2(z_value, x_value))#get angle
            if angle < 0:#angle→(0<=angle<=359.9)
                angle = 360 + angle
        if z_value == -0.0:#angle = -0.0 = 0.0
            angle = 0.0
    return round(angle, 1)# get angle

def set_status():# set status
    data_status = lis.xfer2([lisread | lissingle |status_reg,0x00])
    return data_status[1]#get statsu data

def get_status(data_list):
    #flag 1 = newdata for available
    if data_list[5] == 1:#ZDA
        if data_list[6] == 1:#YDA
            if data_list[7] == 1:#XDA
                screen.addstr('complete set newdata of x-, y-, and z-axes\n\r')
            elif data_list[7] == 0:#XDA
                screen.addstr('complete set newdata of y-axis and z-axis\n\r')
        elif data_list[6] == 0:#YDA
            if data_list[7] == 1:#XDA
                screen.addstr('complete set newdata of x-axis and z-axis\n\r')
            elif data_list[7] == 0:#XDA
                screen.addstr('complete set newdata of z-axis\n\r')
    elif data_list[5] == 0:#ZDA
        if data_list[6] == 1:#YDA
            if data_list[7] == 1:#XDA
                screen.addstr('complete set newdata of x-axis and y-axes\n\r')
            elif data_list[7] == 0:#XDA
                screen.addstr('complete set newdata of y-axis\n\r')
        elif data_list[6] == 0:#YDA
            if data_list[7] == 1:#XDA
                screen.addstr('complete set newdata of x-axis\n\r')
            elif data_list[7] == 0:#XDA
                screen.addstr('complete set newdata of None\n\r')

def print_data(x, y, z):#print(x,y,z )data 
    if x >= 0 and y >= 0 and z >= 0:#all valid
        screen.addstr("x=+" +  str('{:.02f}'.format(x)) +
                      ",y=+" + str('{:.02f}'.format(y)) +
                      ",z=+" + str('{:.02f}'.format(z)) + "\n\r")
    if x >= 0 and y >= 0 and z < 0:#zinvalid only
        screen.addstr("x=+" +  str('{:.02f}'.format(x)) +
                      ",y=+" + str('{:.02f}'.format(y)) +
                      ",z=" + str('{:.02f}'.format(z)) + "\n\r")
    if x >= 0 and y < 0 and z >= 0:#y invalid only
        screen.addstr("x=+" +  str('{:.02f}'.format(x)) +
                      ",y=" + str('{:.02f}'.format(y)) +
                      ",z=+" + str('{:.02f}'.format(z)) + "\n\r")
    if x >= 0 and y < 0 and z < 0:#x valid only
        screen.addstr("x=+" +  str('{:.02f}'.format(x)) +
                      ",y=" + str('{:.02f}'.format(y)) +
                      ",z=" + str('{:.02f}'.format(z)) + "\n\r")
    if x < 0 and y >= 0 and z >= 0:#x invalid only
        screen.addstr("x=" +  str('{:.02f}'.format(x)) +
                      ",y=+" + str('{:.02f}'.format(y)) +
                      ",z=+" + str('{:.02f}'.format(z)) + "\n\r")
    if x < 0 and y >= 0 and z < 0:#y valid only
        screen.addstr("x=" +  str('{:.02f}'.format(x)) +
                      ",y=+" + str('{:.02f}'.format(y)) +
                      ",z=" + str('{:.02f}'.format(z)) + "\n\r")
    if x < 0 and y < 0 and z >= 0:#z valid only
        screen.addstr("x=" +  str('{:.02f}'.format(x)) +
                      ",y=" + str('{:.02f}'.format(y)) +
                      ",z=+" + str('{:.02f}'.format(z)) + "\n\r")
    if x < 0 and y < 0 and z < 0:#all invalid
        screen.addstr("x=" +  str('{:.02f}'.format(x)) +
                      ",y=" + str('{:.02f}'.format(y)) +
                      ",z=" + str('{:.02f}'.format(z)) + "\n\r")
        
def active_lis3dh():
    data = get_axis()#0x20
    data_list = create_list(data)#binary data
    axis_data, scale_data = set_key(data_list)#get axis_data, scale_data
    axis_list = create_list(axis_data)#binary data
    scale_list = create_list(scale_data)#binary data
    status_data = set_status()#get information of status
    status_data_list = create_list(status_data)#binary data
    get_status(status_data_list)#check data readiness
    x = acceleration_value(x_address, scale_list)#get x_acceleration
    y = acceleration_value(y_address, scale_list)#get y_acceleration
    z = acceleration_value(z_address, scale_list)#get z_acceleration
    print_data(x, y, z)#print acceleration
    if axis_list[5] == 1 and axis_list[7] == 1:#get angle
        screen.addstr("I = " + str(search_angle(x_address,z_address,
                        scale_list, axis_list)) + "\n\r")
    if axis_list[5] == 0 or axis_list[7] == 0:#incalculable
        screen.addstr('can not find the angle\n\r')
    screen.addstr(0, 0, '\r')
    time.sleep(1)

try:
    set_lis3dh()
    while True:
        active_lis3dh()
except KeyboardInterrupt:
    pass
curses.nocbreak()
curses.echo()
curses.endwin()

lis.close()