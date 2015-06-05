import urllib2
import json
import os.path
import time
import datetime
import os

def main():
	threshold = 3 # look for magnitude higher or equal to this value

	# Retry to get data from infp for 5 time , sleep 30 seconds in between
	for x in range(0, 5):
		try:
			url = urllib2.urlopen('http://www.infp.ro/data/webSeismicity.json')
			error_fetch = None
		except urllib2.HTTPError, e:
			print(e.code)
			error_fetch = e.code
		except urllib2.URLError, e:
			print(e.args)
			error_fetch = e.code
		if error_fetch:
			from time import sleep
			sleep(30)
			if x == 5: # If this is the last pass here , and we did try 5 times exit program
				exit()
		else:
			break

	j_obj = json.load(url) #Page loaded fine so we can load the json
	
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

def logCutremure(m, r, d, c):
	with open('logs.json', 'r') as f:
		data = json.load(f)
	with open('logs.json','w+') as logFile: #use of with open to open then close imediatly
		data.append({'magnitude':m, 'region': r, 'depth':d, 'created_at':c})
		json.dump(data, logFile, indent=4)
	print "\t log saved"	
	return

try:
	print datetime.datetime.now() #  Print the time when it started running
	
	print "INFP.ro Sniffer \n \n"

	run = raw_input("Mode: Run once or forever  ? [ 'once' , 'forever' ] \n ")
	if run == 'forever':
		while True:
			main()
			time.sleep(1) #sleep for a second
	else:
		main()
except KeyboardInterrupt:
	print datetime.datetime.now() # Print the time on exit
	pass
