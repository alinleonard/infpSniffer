import urllib2
import json
import os.path
import time
import datetime
import os
import random
import httplib
import socket

debug = True

def main(proxy):
	threshold = 3 # look for magnitude higher or equal to this value

	data = fetchData(proxy,5,30) #Use proxy <True,False> , Retry times <int> , Timeout before another retry <int>

	j_obj = loadData(data,proxy,5,30,5,0) #Proxy <True,False>, Fetch data Retry times <int> , Fetch data Timeout <int> , Load data retry <int> , Load data timeout before refech and load <int> 

	magnitude = j_obj['local'][0]['magnitude'] 
	region =  j_obj['local'][0]['region']
	depth = j_obj['local'][0]['depth']
	created_at = j_obj['local'][0]['dt_rom']

	# if we don't have magnitude to work with in json then it means we did not load corectly , we exit program
	if not magnitude:
		print "NO MAGNITUDE TO READ FROM"
		exit()
	
	if os.path.exists('logs.json') and magnitude >= threshold:
		with open('logs.json') as data_file:
			j_obj_file = json.load(data_file)
		#get the last index of the log so we can compare
		last = 0
		for number in j_obj_file:
			last = last + 1
			
		if j_obj_file[last-1]['created_at']: #if we have data to work with ( if file is not empty )
			if j_obj_file[last-1]['created_at']	!= created_at: # so we don't save it multiple times
				print "CUTREMUR (new entry)"
				logCutremure(magnitude, region, depth, created_at)
		else: # there is no data to work with so we add now
			print "CUTREMUR (no data , new entry)"
			logCutremure(magnitude, region, depth, created_at)
	else: # there is no file
		if magnitude >= threshold:
			with open('logs.json','w') as logFile:
				json.dump([{'magnitude':magnitude, 'region': region, 'depth':depth, 'created_at':created_at}], logFile, indent=4)
				print "CUTREMUR (no file , new file and data)"

	os.system('cls' if os.name == 'nt' else 'clear') # clear screen

	print "Ultimul cutremur: \n"
	print "Magnitudine : %s - %s - %s km - %s \n" % (magnitude, region, depth, created_at)

	return


def loadData(data,proxy,fdataR,fdataT,retry,timeout):
	for x in range(0, retry): #Sometimes the data of the json is not loaded correct , we reload the page and load again
		try:
			with open('cache.json','r') as data_file:
				j_obj = json.load(data_file)		
		except ValueError, e: #invalid json
			json_error = "error"
			if debug:
				print "\t\t---triggered expect ValueError, e in loadData---\n\t---error triggered: %s --- " % (e)
			time.sleep(timeout)
		else: #valid json
			json_error = None
			break #break for loop
		
		if json_error and x == retry:
			print "Json could not be loaded corectly"
			exit()

		if json_error:
			if debug:
				print "\t\t--- in loadData , json_error = true ---"
			data = fetchData(proxy,fdataR,fdataT)

	return j_obj

def fetchData(proxy,retry,timeout):

	if not proxy:
		for x in range(0, retry): # Retry to get data from infp for <retry> time , sleep <timeout> seconds in between
			try:
				data = urllib2.urlopen('http://www.infp.ro/data/webSeismicity.json')
				error_fetch = None
			except urllib2.HTTPError, e:
				if e.code:
					print(e.code)
					error_fetch = e.code
				else:
					error_fetch = "HTTPError"
					print error_fetch
			except urllib2.URLError, e:
				if e.args:
					print(e.args)
					error_fetch = e.code
				else:
					error_fetch = "URLError"
					print error_fetch
			if error_fetch:
				time.sleep(timeout)
				if x == retry: # If this is the last pass here , and we did try <retry> times exit the program
					exit()
			else:
				break
	else:
		data = setProxy()
		if not data:
			print "no proxy to work with!"
			exit()
	

	return data

def logCutremure(m, r, d, c):
	with open('logs.json', 'r') as f: #read the content of the file so we can append later on
		data = json.load(f)
	with open('logs.json','w+') as logFile: #we use <with open> so the file will close after we use it
		data.append({'magnitude':m, 'region': r, 'depth':d, 'created_at':c})
		json.dump(data, logFile, indent=4)
	print "\t log saved"	
	return

#Load and connect to proxies
def setProxy():

	with open('proxy.txt','r') as proxys:
		proxy = proxys.readlines()
	if len(proxy) > 0:
		for x in range(0, len(proxy)-1):
			try:
				rnd = random.randint(0,len(proxy)-1)

				if debug:
					print "try Proxy : %s time , random numer: %s proxy used to load %s " % (x,rnd,proxy[rnd])
					
				proxyHandler = urllib2.ProxyHandler({'http': proxy[rnd]})
				opener = urllib2.build_opener(proxyHandler)
				urllib2.install_opener(opener)
				s = urllib2.urlopen(
					"http://www.infp.ro/data/webSeismicity.json",
					timeout=5
					)

				with open('cache.json', 'w+') as data_file:
					data_file.write(s.read())
				
				s.close()
			except (IOError, httplib.HTTPException):
				saveNWProxies(proxy[x])
				#time.sleep(5) sleep may be needed so we don't get banned on proxis
				s = None
			except socket.timeout:
				s = None
			else:
				break
	else:
		s = None

	return s

#Save in a file the proxies that don't connect
def saveNWProxies(address):
	with open('nwProxy.txt','a+') as myFile:
		myFile.write(address)
	return

def clearNWProxies():
	with open('nwProxy.txt','r') as myFile: #read and save a list with not working proxies
		proxyNW = myFile.readlines()

	with open('proxy.txt','r') as myFile: #read and save a list with all proxies
		proxy = myFile.readlines()

	print "Total proxies before clean: " , len(proxy)

	open('proxy.txt' , 'w').close()

	newProxy = []
	x = 0

	proxy = list(set(proxy)) #remove duplicates

	while (x <= len(proxy)-1):
		for y in range(0, len(proxyNW)-1):
			#print "X: %s Y: %s" % (x,y)
			if(proxy[x] == proxyNW[y]):
				newProxy.append(proxy[x])
				break
		x = x + 1

	with open('proxy.txt','a+') as myFile:
		for item in newProxy:
			myFile.write("%s" % item)

	print "Total proxies after clean: " , len(newProxy)

	return


#How to use the program
#sudo python earthquake.py

try:
	complete = 0 #number of times the program has completed the program

	timeRun = datetime.datetime.now() #use this time on exit
	startTime = time.time() #use this time on exit
	
	print "INFP.ro Sniffer \n \n"

	clear = raw_input("Do you want to clear the bad proxies? <yes,no> \n")
	if clear == 'yes':
		print "clearing..."
		clearNWProxies()

	mode = raw_input("Run once or scan forever ? <once,forever> \n ")
	useProxy = raw_input("Do you want to use proxy? <yes,no> \n ")

	#Interpret the inputs
	if mode == 'forever':
		if useProxy == 'yes': # use proxy
			while True:
				main(True)
				time.sleep(1) #sleep for a second , we may not need it for proxy
				if debug:
					complete = complete + 1
		else: # don't use proxy
			while True:
				main(False)
				time.sleep(1) #sleep for a second
	else:
		if useProxy == 'yes':
			main(True)
		else:
			main(False)

except KeyboardInterrupt:
	if debug:
		print "The program completed in forever mode : %s times" % (complete)
	# Print the time on exit
	print "\nProgram has started running at : %s " % (timeRun)
	print "Program has stopped running at : %s " % (datetime.datetime.now()) 
	print "---- Program runned for %s seconds ---- " % (time.time() - startTime)
	pass
