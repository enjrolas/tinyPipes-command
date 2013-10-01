import serial
import time

def checkBytes():
    print ser.inWaiting()
    while ser.inWaiting()>0:
        print(ser.read())



ser=serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=19200)

'''ser.write("AT\r\n")
time.sleep(1)
checkBytes()
'''
number="+8613632651167"
ser.write("AT+CMGF=1\r")    #Because we want to send the SMS in text mode
delay(100)
ser.print("AT+CMGS=\"")
ser.print(number)
ser.print("\"") #send sms message, be careful need to add a country code before the cellphone number
delay(100);
ser.print(message) #the content of the message
ser.print("\"")
delay(100)
ser.println((char)26) #//the ASCII code of the ctrl+z is 26
delay(100)
ser.println()

ser.close()

