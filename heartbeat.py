import urllib
import urllib2
import os
import time
from netifaces import interfaces, ifaddresses, AF_INET

addresses = [i['addr'] for i in ifaddresses("eth0").setdefault(AF_INET, [{'addr':'No IP addr'}] )]
ipAddress=addresses[0]
sprinklerId=1

myURL = "http://valve.tinyPipes.net/heartbeat/%s/" % (sprinklerId)
print myURL
while(True):
#    urllib2.urlopen(myURL).read()
    try:
        print urllib2.urlopen(myURL).read()
    except:
        print "well, something happened"
    time.sleep(5)
