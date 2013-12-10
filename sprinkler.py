#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb
import sys
import serial
import time
import re
import sys, traceback
import pickle
import urllib, urllib2

def addMessage(sprinklerId, origin, content):
    print "adding message to database"
    with spfdb:
        cur = spfdb.cursor()
        query="select * from pipe_pipe where phoneNumber=\"%s\"" % origin
        cur.execute(query)
        if cur.rowcount>0:  #this is from one of our pipes
            row=fetchoneDict(cur)
            pipeId=row['id']
            messageType="squirt"
        else:
            pipeId="0"
            messageType="unknown incoming"
        query="INSERT into communications_squirt(sprinkler_id, messageType, content, origin, timeStamp) values ('%s', '%s', '%s', '%s', NOW())" % (sprinklerId, messageType, content, origin)
        cur.execute(query)

def checkResponse(delay):
    time.sleep(delay)
    line=""
    while ser.inWaiting()>0:
        line=readLine()
        print line

def readLine():
    line=""
    while ser.inWaiting()>0:
        incoming=ser.read()
        line+=incoming
        if incoming=='\n':
            break
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
    messages=[]
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
                messages.append(message)
                print ""
    for message in messages:
        print message
    ser.write("AT+CMGDA=\"DEL READ\"\r\n")
    checkResponse(1)
    return messages

def textMessage(number, message):
    print "sending \"%s\" to %s" % (message, number)
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
    checkResponse(4)  # wait four seconds after sending to give time for everything to percolate

def listAllMessages():
    ser.write("AT+CMGL=\"ALL\"\r\n")
    checkResponse(5)

def connect(number):
    textMessage(number, "connect")

def disconnect(number):
    textMessage(number, "disconnect")

def restart():
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print output


def fetchoneDict(cursor):
    row = cursor.fetchone()
    if row is None: return None
    cols = [ d[0] for d in cursor.description ]
    return dict(zip(cols, row))

def flushReceiveBuffer():
    while(True):
        time.sleep(.1)
        bytes_in_buffer = ser.inWaiting()
        if(bytes_in_buffer == 0):
            break
        print(ser.read(bytes_in_buffer))


def getPhoneNumber():
    ser.write("AT+CNUM\r\n")
    time.sleep(1)
    number=""
    while ser.inWaiting()>0:
        line=readLine().strip()
        print line
        if line.find("+CNUM:")!=-1:
            number=line[find_nth(line, ",", 1)+1: find_nth(line, ",", 2)]
            number=number.replace('"', '')
            print number
    return number

def getSprinklerId(number):
    with spfdb:
        cur = spfdb.cursor()
        query="select * from sprinkler_sprinkler where phoneNumber like \"%"
        query+=number
        query+="%\""
        cur.execute(query)
        if cur.rowcount>0:  #this is from one of our existing sprinklers
            row=fetchoneDict(cur)
            sprinklerId=row['id']
            return sprinklerId
        else:
            return "0"

def pullCommands():
    print("checking database")
    with spfdb:
        cur = spfdb.cursor()
        cur.execute("select * from communications_spray where sent=\"0\"")
        try:
            row = fetchoneDict(cur)
            print row
            id=row['id']
            to=row['destination']
            message=row['content']
            textMessage(to, message)
            str = "UPDATE communications_spray set sent=\"1\" where id='%s'" % id
            cur.execute(str)

        except Exception as e:   # no waiting commands                                                                                                                     
            print "no pending commands"



ser = None
port = "/dev/ttyUSB0"
if  __debug__:
    for tries in range(1,5):
        try:
            print("Establishing connection with GSM module through port " + port)
            ser = serial.Serial(port, 19200)
        except: 
            pass
        if ser is None:
            print("Cannot establish connection with GSM module. Exiting.")
            sys.exit()
    print("GSM module found! Connection established.")

listAllMessages()

'''database-specific info is stored in a separate file called 'db'.  The file stores the host, 
the port, the user, password and database.  The values are separated
from the names by a colon, as follows:
host: buckaroobonzai.cc
port: 3306
user: jonBigBootay
password: ssshSecretDontTellAnyone
db: hongKongCavaliers
'''

f=open('db','r')
lines = f.readlines()
host=lines[0].split(':')[1].strip()
port=int(lines[1].split(':')[1].strip())
user=lines[2].split(':')[1].strip()
password=lines[3].split(':')[1].strip()
database=lines[4].split(':')[1].strip()

print("connecting to database....")
spfdb = MySQLdb.connect(host=host,port=port,user=user,passwd=password,db=database)
print("connected!  Having a look around..")
cur = spfdb.cursor()
cur.execute("show tables")
results=cur.fetchall()
for table in results:
    print table

checkResponse(1)
flushReceiveBuffer()
sprinklerPhoneNumber=getPhoneNumber()
sprinklerId=getSprinklerId(sprinklerPhoneNumber)

try:    
    print "sprinker phone number:  %s" % sprinklerPhoneNumber
    print "sprinklerId: %s" % sprinklerId
    if __debug__:
        print("initialized and ready to go")

    while(True):
        pullCommands()
        checkResponse(1)
        messages=checkMessages()
        for message in messages:
            print message[1]
            addMessage(sprinklerId, message[1], message[2])
            
except KeyboardInterrupt:
    print "see ya"
