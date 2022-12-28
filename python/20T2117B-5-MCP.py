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

single_end_0 = 0x68#ch0 IN+
single_end_1 = 0x78#ch1 IN+
pseudo_0 = 0x48#ch0 IN+, ch1 IN-
pseudo_1 = 0x58#ch0 IN-, ch1 IN +

def set_mcp3002():#set mcp3002
    lis.open(0,1)#SPIO CE1
    lis.bits_per_word = 8#word = 8bit
    lis.max_speed_hz = 1000000

def change_mode(command_list):#change mode
    change_command = 0x00
    #Single-EndedMode→Pseudo-DifferentialMode
    if command_list[2] == 1:#SGL/SIGN
        if command_list[3] == 0:#ch0 IN+, ch1 IN-
            change_command = pseudo_0
            screen.addstr("change_command is 0x48\n\r")
        elif command_list[3] == 1:#ch0 IN-, ch1 IN+
            change_command = pseudo_1
            screen.addstr("change_command is 0x58\n\r")
    #DifferentialMode-Single-EndedMode→Pseudo
    elif command_list[2] == 0:#SSGL/SIGN
        if command_list[3] == 0:#ch0 +
            change_command = single_end_0
            screen.addstr("change_command is 0x68\n\r")
        elif command_list[3] == 1:#ch1 +
            change_command = single_end_1
            screen.addstr("change_command is 0x78\n\r")
    return change_command #get command

def change_setting_mode(command_list):
    change_command = 0x00
    if command_list[3] == 1:#ODD/SIGN
        if command_list[2] == 0:#pseudo_1→pseudo_0
            change_command = pseudo_0
            screen.addstr("change_command is 0x48\n\r")
        elif command_list[2] == 1:
            change_command = single_end_0#single_end_1→single_end_0
            screen.addstr("change_command is 0x68\n\r")
    elif command_list[3] == 0:#ODD/SIGN
        if command_list[2] == 0:
            change_command = pseudo_1#pseudo_0→pseudo_1
            screen.addstr("change_command is 0x58\n\r")
        elif command_list[2] == 1:
            change_command = single_end_1#single_end_0→single_end_1
            screen.addstr("change_command is 0x78\n\r")
    return change_command#get command

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

def msbf(command):#get data
    vdd = 5
    rcv = lis.xfer2([command,0x00])#10bit 0~1023
    ad =(((rcv[0]&0x03)<<8)+rcv[1])#10bit data
    vin = (ad * vdd) /1024#get vin data
    screen.addstr("analog input voltage is " + str(vin) + "V\n\r")

def mcp_set_key(command, command_list):#set key event
    get_command = command
    keyInput = screen.getch() #get keystrokes as ASCII digits
    if keyInput == ord('m'):#if get letter'm' from keyboard
        get_command = change_mode(command_list)#SGL/DIFF
    if keyInput == ord('c'):#if get letter'c' from keyboard
        get_command = change_setting_mode(command_list)#ODD/SIGN
    if keyInput == ord('r'):#if get letter'r' from keyboard
        msbf(command)#print vin
    return get_command # get command
  
def active_mcp3002(command):
    screen.addstr("command of mcp3002 is " + str(command) + "\n\r")
    command_list = create_list(command)#create command_list
    command = mcp_set_key(command, command_list)#key event
    screen.addstr(0,0, '\r')
    time.sleep(1)
    return command# get command

try:
    set_mcp3002()
    command = single_end_0
    while True:
        command = active_mcp3002(command)
except KeyboardInterrupt:
    pass

curses.nocbreak()
curses.echo()
curses.endwin()

lis.close()