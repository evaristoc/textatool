#!/usr/bin/env python
"""
description:
"""

import sys, os

from dotenv import load_dotenv
load_dotenv(dotenv_path='../.env')
load_dotenv()

import pickle, json
import stomp
import time
import processingData
import collections, itertools, copy, operator



print(os.getenv("TEST_MULTILINE_VAR"))
#sys.exit()

done = False

# Set Apollo Username/Password
#apollo_user = os.getenv("ActiveMQUSER")
#apollo_pass = os.getenv("ActiveMQPASS")

class MyListener(object):
	def __init__(self):
		self.done = False
		print("Connected to Apache Apollo")
	def on_error(self, headers, message):
		print('received an error')
	def on_message(self, headers, message):
		if(self.done == False):
			otp = json.loads(message)
			print(len(otp))
			al, nor, fd = processingData.allrecordsLemmatization(processingData.allrecordsPreparation(otp))
			#fn = processingData.jsonbuilding(al, nor, fd)
			fn = processingData.jsonbuildingnew(al, nor, processingData.wordimportance_var2(nor,fd))
			for rcd in fn:
				print(rcd['author'])
				conn.send(body=json.dumps(rcd), destination='/queue/withPython')
			self.done = True
	def on_disconnected(self):
		print("Connecting to Apollo")	

conn = stomp.Connection([(os.getenv("ActiveMQHOST"),os.getenv("ActiveMQPORT"))])
conn.set_listener('', MyListener())
conn.start()
conn.connect(os.getenv("ActiveMQUSER"), os.getenv("ActiveMQPASS"))
connected = True

conn.subscribe(destination='/queue/inPython', id=1)

# Keeps this script going on an endless loop
def runServer():
	print("Process Text Analyser Script Now Running....")
	while 1:
		time.sleep(10)
		
if connected:
	runServer()

# conn.disconnect()

##################
## Previous data Preparation
#################

# with open(os.getcwd()+'/1_archive/data_foundjob.pkl', 'rb') as f_in:
#     data_saved = pickle.load(f_in)
# 
# for u in data_saved:
#     if data_saved[u]['forum']['foundjob_msg']['text'] != '':
#         print(data_saved[u]['forum']['foundjob_msg']['text'])
#         break
# 
# 
# for u in data_saved:
#     if data_saved[u]['forum']['foundjob_msg']['text'] != '':
#         soup_forum = BeautifulSoup(data_saved[u]['forum']['foundjob_msg']['text'])
#         break

