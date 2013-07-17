import urllib
import urllib2
import os
import time
from netifaces import interfaces, ifaddresses, AF_INET

addresses = [i['addr'] for i in ifaddresses("eth0").setdefault(AF_INET, [{'addr':'No IP addr'}] )]
IP_address=addresses[0]

myParameters = { "IP address" : IP_address}
myURL = "http://artiswrong.com/tinyPipes?%s" % urllib.urlencode(myParameters)

while(True):
    urllib2.urlopen(myURL).read()
    time.sleep(60)
