import urllib2
import json
import os.path
import time
import datetime

def logCutremure(m, r, d, c):
	fisier =  open('logs.json','a+')
	json.dump({'magnitude':m, 'region': r, 'depth':d, 'created_at':c}, fisier, indent=4)
	print "\t log saved"	
	return
try:
	print "INFP.ro Sniffer"
	print datetime.datetime.now()
	while True:
		url = urllib2.urlopen('http://www.infp.ro/data/webSeismicity.json')
		j_obj = json.load(url)
	
		magnitude = j_obj['local'][0]['magnitude'] 
		region =  j_obj['local'][0]['region']
		depth = j_obj['local'][0]['depth']
		created_at = j_obj['local'][0]['dt_rom']
	
		#print "Ultimul cutremur: \n"
		#print "%s - %s - %s km - %s \n" % (magnitude, region, depth, created_at)


		if os.path.exists('json-dump.json'):
			#print "\n\t file exists..."
			with open('json-dump.json') as data_file:
				j_obj_old = json.load(data_file)
			#print "\t ultimul cutremur salvat: %s - %s Mag" % (j_obj_old['local'][0]['dt_rom'],j_obj_old['local'][0]['magnitude'])
			if j_obj_old['local'][0]['dt_rom'] != created_at and magnitude >= 4:
				print "\nCUTREMUR (updated)" 
				file = open('json-dump.json','w+')
				json.dump(j_obj, file)
				logCutremure(magnitude, region, depth, created_at)
		if not os.path.exists('json-dump.json') and magnitude >= 4:
			print "CUTREMUR (saved)"
			file = open('json-dump.json','w+')
			json.dump(j_obj, file)
			logCutremure(magnitude, region, depth, created_at)
		time.sleep( 1 )
		#print "\n\n end"
except KeyboardInterrupt:
	print datetime.datetime.now()
	pass
