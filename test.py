import serial
import sys
import time

def checkResponse(delay):
    time.sleep(delay)
    while ser.inWaiting()>0:
        sys.stdout.write(ser.read())        
        sys.stdout.flush()

def textMessage(number, message):
    ser.write("AT+CMGF=1\r\n")  # we want to send the SMS in text mode
    checkResponse(0.5)
    ser.write("AT+CMGS=\"")
    ser.write(number)
    ser.write("\"\r\n") #send sms message, be careful need to add a country code before the cellphone number
    checkResponse(0.5)
    ser.write(message + "\r\n") #the content of the message
    time.sleep(1)
    ser.write(chr(26)+"\r\n")
    ser.write("\r\n")
    checkResponse(1)

def connect(number):
    textMessage(number, "connect")

def disconnect(number):
    textMessage(number, "disconnect")

def deleteAll():
    
    ser.write("AT+CMGF=1\r\n")
    checkResponse(1)
    
#    ser.write("AT+CMGDA=\"DEL READ\"\r\n")
#    checkResponse(1)
    ser.write("AT+CMGDA=\"DEL SENT\"\r\n")
    checkResponse(1)
    
    ser.write("AT+CMGL=\"ALL\"\r\n")
    checkResponse(5)
    '''
    for i in range(0,50):      
        ser.write("AT+CMGR=%d\r\n" %i)
        checkResponse(1)
        ser.write("AT+CMGD=%d\r\n" % i)
        checkResponse(0.5)
     '''

def readLine():
    line=""
    while ser.inWaiting()>0:
        incoming=ser.read()
        line+=incoming
        if incoming=='\n':
            break
    line=line.strip()
    return line

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def deleteMessage(index):
    print("deleting message #: %s" % index)
    ser.write("AT+CMGD=%s\r\n" % index)



def checkMessages():
    ser.write("AT+CMGL=\"ALL\"\r\n")
    time.sleep(3)
    line=" "
    messages=()
    while ser.inWaiting()>0:
        line=readLine()
        if line.find("+CMGL")!=-1:
            if line.find("AT+CMGL")==-1:
                messageIndex=line[line.find(':')+1:line.find(',')].strip()
                print "message index: %s" % messageIndex
                number=line[find_nth(line, ",", 2)+1: find_nth(line, ",", 3)]
                number=number.replace('"', '')
                print "from: %s" % number
                content=readLine()
                print "message: %s" % content
                message=(messageIndex, number, content)
                messages+=message
                print ""
   
#    ser.write("AT+CMGDA=\"DEL READ\"\r\n")
#    checkResponse(1)

def getPhoneNumber():
    ser.write("AT+CNUM\r\n")
    time.sleep(3)
    line=" "
    number=""
    while ser.inWaiting()>0:
        line=readLine()
        print("line:  %s" % line)
        if line.find("+CNUM:")!=-1:
            number=line[find_nth(line, ",", 1)+1: find_nth(line, ",", 2)]
            number=number.replace('"', '')
            print number
        return number

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
#    port='/dev/tty.usbserial-A400fZ6T',
#    port='/dev/tty.usbserial-A6007ZCF',
    port='/dev/ttyUSB0',
    baudrate=19200,
)



if ser.isOpen():
    ser.close()
ser.open()
ser.isOpen()
time.sleep(2)
'''
sprinklerPhoneNumber=getPhoneNumber()
if sprinklerPhoneNumber!="":
    getSprinklerId(sprinklerPhoneNumber)
else:
    sprinklerId=0
'''
checkMessages()
#deleteAll()
#connect("+8613632650805")
#disconnect("+8613632650805")
#connect("+8615013784414")
#disconnect("+8615013784414")
