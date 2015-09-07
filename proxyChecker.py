import gevent

from gevent import monkey

monkey.patch_socket()
#monkey.patch_all()

import urllib2
import httplib
import time

with open('proxy.txt','r') as myFile:
	proxys = myFile.readlines()

proxys = set(proxys)

def checkProxy(proxy,number):
	print "checking proxy: %s " % (proxy)
	try:
		proxyHandler = urllib2.ProxyHandler({'http': proxy})
		opener = urllib2.build_opener(proxyHandler)
		urllib2.install_opener(opener)
		s = urllib2.urlopen(
					"http://www.infp.ro/data/webSeismicity.json",
					timeout=5
		)
		s.close()
		print "\t %s :it's ok" % (proxy)
	except (IOError, httplib.HTTPException):
		print "\t %s :proxy not connecting..." % (proxy)
		saveNWProxies(proxy)
	except socket.timeout:
		print "time out"

def saveNWProxies(address):
	with open('nwProxy.txt','a+') as myFile:
		myFile.write(address)
	return

#jobs = [gevent.spawn(checkProxy, proxy) for proxy in proxys]
#gevent.joinall(jobs)

jobs = []
x = 0
for proxy in proxys:
	if x<1000:
		jobs.append(gevent.spawn(checkProxy, proxy, x))
		x = x+1

jobTask0 = gevent.joinall(jobs)

if gevent.wait(jobTask0):
	print "done the first 1000 , waiting 5 seconds before starting again"
	time.sleep(5)
	jobs = []
	x = 0
	for proxy in proxys:
		if x>=1000:
			jobs.append(gevent.spawn(checkProxy, proxy, x))
		x = x+1
			
	jobTask1 = gevent.joinall(jobs)

	if gevent.wait(jobTask1):
		print "\n\nFinished!"
