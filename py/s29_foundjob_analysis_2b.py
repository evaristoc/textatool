#!/usr/bin/env python
"""
description:
"""

import sys, os
import pickle, json
import stomp
import time
import processingData
import collections, itertools, copy, operator


done = False

# Set Apollo Username/Password
apollo_user = "TOFILLIN"
apollo_pass = "TOFILLIN"

class MyListener(object):
	def __init__(self):
		self.done = False
		print("Connected to Apache Apollo")
	def on_error(self, headers, message):
		print('received an error')
	def on_message(self, headers, message):
		if(self.done == False):
			otp = json.loads(message)
			fn = processDataFunctionality(otp)
			conn.send(body=json.dump(fn), destination='/queue/fromPython')
			self.done = True
	def on_disconnected(self):
		print("Connecting to Apollo")	

conn = stomp.Connection([('TO.FILL.IN',34534543523325)])
conn.set_listener('', MyListener())
conn.start()
conn.connect(apollo_user, apollo_pass)
connected = True

conn.subscribe(destination='/queue/toPython', id=1)

# Keeps this script going on an endless loop
def runServer():
	print("Process Cards Printer Script Now Running....")
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

